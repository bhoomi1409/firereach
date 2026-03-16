"""
FireReach Orchestrator v3 — Fully Autonomous
Input:  ICP (3 plain English strings) + max_companies int
Output: BatchOutreachResult

Pipeline:
  Step 0: Discover companies from ICP via Serper
  Step 1: Enrich each company (Hunter + Serper)
  Step 2: Score ICP fit — skip below threshold
  Step 3: Harvest signals (NewsAPI + Serper)
  Step 4: Find contact (Hunter T1/T2/T3/generic)
  Step 5: Generate email (Groq LLM)
  Step 6: Send (Gmail SMTP)

No Apollo. Hunter is T1. User only provides ICP.
"""

import os
import re
import math
import asyncio
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional

import httpx
from pydantic import BaseModel

from company_discovery import discover_companies

# ── ENV KEYS ──────────────────────────────────────────────────────────────────

HUNTER_KEY  = os.getenv("HUNTER_API_KEY",      "")
GROQ_KEY    = os.getenv("GROQ_API_KEY",         "")
NEWSAPI_KEY = os.getenv("NEWS_API_KEY",          "")
SERPER_KEY  = os.getenv("SERPER_API_KEY",        "")
SMTP_USER   = os.getenv("SMTP_USER",             "")
SMTP_PASS   = os.getenv("SMTP_APP_PASSWORD",     "")

# ── RESPONSE MODELS ───────────────────────────────────────────────────────────

class OutreachResult(BaseModel):
    company_name:   str
    icp_score:      float
    should_send:    bool
    skip_reason:    Optional[str] = None
    contact_email:  Optional[str] = None
    contact_name:   Optional[str] = None
    contact_title:  Optional[str] = None
    top_signals:    list[str] = []
    email_subject:  Optional[str] = None
    email_body:     Optional[str] = None
    ppt_generated:  bool = False
    ppt_filename:   Optional[str] = None
    sent:           bool = False
    send_message:   str = ""
    log:            list[str] = []

class SkippedCompany(BaseModel):
    company_name: str
    skip_reason:  str

class BatchOutreachResult(BaseModel):
    batch_id:               str
    icp_summary:            str
    companies_discovered:   int
    companies_scored:       int
    companies_passed_icp:   int
    companies_contacted:    int
    results:                list[OutreachResult] = []
    skipped:                list[SkippedCompany] = []

# ── SEMANTIC ENGINE ───────────────────────────────────────────────────────────

_SYNS = {
    "saas":       ["software", "cloud", "b2b software", "subscription", "platform"],
    "fintech":    ["payments", "banking", "financial", "lending"],
    "startup":    ["early stage", "seed", "series a", "growing"],
    "hiring":     ["recruiting", "job posting", "open roles", "headcount"],
    "funding":    ["raised", "investment", "series", "venture", "backed"],
    "automation": ["automate", "ai", "workflow", "efficiency"],
    "pipeline":   ["sales pipeline", "deals", "opportunities", "revenue"],
}

def _expand(text: str) -> str:
    t = text.lower()
    extra = []
    for k, v in _SYNS.items():
        if k in t:
            extra.extend(v)
    return t + " " + " ".join(extra)

def _vec(text: str) -> dict:
    toks = re.findall(r'\b[a-z0-9]+\b', _expand(text))
    if not toks:
        return {}
    freq: dict = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    n = len(toks)
    return {t: c / n for t, c in freq.items()}

def _sim(a: str, b: str) -> float:
    va, vb = _vec(a), _vec(b)
    keys   = set(va) | set(vb)
    dot    = sum(va.get(k, 0) * vb.get(k, 0) for k in keys)
    ma     = math.sqrt(sum(v * v for v in va.values()))
    mb     = math.sqrt(sum(v * v for v in vb.values()))
    return dot / (ma * mb) if ma and mb else 0.0

# ── KEYWORD EXTRACTOR ─────────────────────────────────────────────────────────

_INDUSTRY_TERMS = [
    "saas", "software", "fintech", "healthtech", "edtech", "ai",
    "machine learning", "payments", "banking", "hr", "recruiting",
    "security", "cloud", "data", "analytics", "ecommerce",
    "marketplace", "platform", "b2b", "enterprise"
]

def _extract_keywords(snippets: list[str]) -> list[str]:
    text = " ".join(snippets).lower()
    return [t for t in _INDUSTRY_TERMS if t in text][:10]

# ── STEP 1: ENRICH ONE COMPANY ────────────────────────────────────────────────

async def _enrich_company(
    name: str,
    what_we_do: str,
    what_they_do: str,
    why_they_need_us: str,
    log: list
) -> dict:
    """
    Enrich a single company using Serper (domain + description) and
    Hunter domain-search (verify domain + get email list).
    Returns company dict with hunter_emails[] populated.
    """
    log.append(f"[Enrich] '{name}'")

    result = {
        "name":          name,
        "domain":        "",
        "industry":      "",
        "headcount":     None,
        "funding":       "",
        "description":   "",
        "keywords":      [],
        "technologies":  [],
        "hunter_emails": []
    }

    # Serper: get domain + description + keywords
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": f"{name} company employees funding industry", "num": 5}
            )
            r.raise_for_status()
            organic  = r.json().get("organic", [])
            snippets = [x.get("snippet", "") for x in organic]

            # Extract domain: first URL whose netloc contains company slug
            name_slug = re.sub(r'[^a-z0-9]', '', name.lower())[:6]
            for item in organic:
                netloc = urlparse(item.get("link", "")).netloc.replace("www.", "")
                if name_slug in netloc.replace(".", ""):
                    result["domain"] = netloc
                    break

            # Fallback domain guess
            if not result["domain"]:
                result["domain"] = f"{re.sub(r'[^a-z0-9]', '', name.lower())}.com"

            result["description"] = " ".join(snippets[:2])
            result["keywords"]    = _extract_keywords(snippets)

            # Try to detect funding from snippets
            funding_patterns = {
                "series_b": ["series b", "series-b"],
                "series_c": ["series c", "series-c"],
                "series_a": ["series a", "series-a"],
                "series_d": ["series d", "series-d"],
                "seed":     ["seed round", "seed funding"],
            }
            desc_lower = result["description"].lower()
            for stage, patterns in funding_patterns.items():
                if any(p in desc_lower for p in patterns):
                    result["funding"] = stage
                    break

            log.append(f"[Enrich] domain={result['domain']} funding={result['funding']}")
    except Exception as e:
        log.append(f"[Enrich] Serper failed for {name}: {e}")
        result["domain"] = f"{re.sub(r'[^a-z0-9]', '', name.lower())}.com"

    # Hunter domain-search: verify domain + pre-fetch email list
    if result["domain"]:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(
                    "https://api.hunter.io/v2/domain-search",
                    params={
                        "domain":   result["domain"],
                        "api_key":  HUNTER_KEY,
                        "limit":    10,
                        "type":     "personal"
                    }
                )
                r.raise_for_status()
                data                  = r.json().get("data", {})
                result["name"]        = data.get("organization") or name
                result["hunter_emails"] = data.get("emails", [])
                log.append(f"[Enrich] Hunter: {len(result['hunter_emails'])} emails")
        except Exception as e:
            log.append(f"[Enrich] Hunter failed for {name}: {e}")

    return result

# ── STEP 2: ICP SCORE ─────────────────────────────────────────────────────────

def _compute_icp_score(
    company: dict,
    what_they_do: str,
    why_they_need_us: str,
    min_headcount: int,
    max_headcount: int,
    good_funding: list[str],
    threshold: int,
    log: list
) -> tuple[float, str]:
    corpus = " ".join([
        company.get("description", ""),
        company.get("industry",    ""),
        " ".join(company.get("keywords",     [])),
        " ".join(company.get("technologies", [])),
    ])

    fit_sim  = _sim(what_they_do,     corpus)
    pain_sim = _sim(why_they_need_us, corpus)

    struct = 0
    hc = company.get("headcount") or 0
    if min_headcount <= hc <= max_headcount:
        struct += 12
    elif hc > 0:
        struct += 4
    fs = (company.get("funding", "")).lower().replace(" ", "_")
    if fs in good_funding:
        struct += 8
    elif fs in ["seed", "series_d"]:
        struct += 4

    total  = round(min(100, fit_sim * 40 + pain_sim * 40 + struct), 1)
    reason = f"fit={fit_sim:.0%} pain={pain_sim:.0%} struct={struct}/20"
    log.append(f"[Score] {company['name']}: {total} ({reason})")
    return total, reason

# ── STEP 3: HARVEST SIGNALS ───────────────────────────────────────────────────

async def _harvest_signals(
    company: dict,
    icp_text: str,
    log: list
) -> list[dict]:
    name    = company.get("name", "")
    signals = []

    # NewsAPI
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(
                "https://newsapi.org/v2/everything",
                params={"q": name, "sortBy": "publishedAt",
                        "pageSize": 3, "apiKey": NEWSAPI_KEY}
            )
            for a in r.json().get("articles", []):
                signals.append({
                    "type":         "news",
                    "summary":      a.get("title", ""),
                    "detected_at":  a.get("publishedAt", datetime.utcnow().isoformat())
                })
    except Exception as e:
        log.append(f"[Signals] NewsAPI failed for {name}: {e}")

    # Serper web
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": f"{name} funding OR expansion OR launch 2025", "num": 3}
            )
            for item in r.json().get("organic", []):
                signals.append({
                    "type":        "web",
                    "summary":     item.get("snippet", ""),
                    "detected_at": datetime.utcnow().isoformat()
                })
    except Exception as e:
        log.append(f"[Signals] Serper web failed for {name}: {e}")

    # Serper jobs (replaces Apollo job_postings)
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": f'"{name}" "is hiring" engineer OR developer OR AI', "num": 5}
            )
            for item in r.json().get("organic", []):
                link    = item.get("link", "")
                snippet = item.get("snippet", "")
                if any(bd in link for bd in ["indeed.com", "glassdoor.com", "ziprecruiter"]):
                    continue
                if len(snippet) > 40:
                    signals.append({
                        "type":        "hiring",
                        "summary":     f"Hiring: {snippet[:100]}",
                        "detected_at": datetime.utcnow().isoformat()
                    })
    except Exception as e:
        log.append(f"[Signals] Serper jobs failed for {name}: {e}")

    # Rerank
    TYPE_W = {"funding": 1.0, "exec_hire": 0.9, "hiring": 0.8, "news": 0.6, "web": 0.5}

    def freshness(dt_str: str) -> float:
        try:
            dt   = datetime.fromisoformat(dt_str.replace("Z", "").split("+")[0])
            days = (datetime.utcnow() - dt).days
            return max(0.0, 1.0 - days / 90)
        except Exception:
            return 0.5

    for s in signals:
        tw = TYPE_W.get(s["type"], 0.5)
        fr = freshness(s.get("detected_at", ""))
        rl = _sim(s.get("summary", ""), icp_text)
        s["_score"] = round(tw * 0.30 + fr * 0.35 + rl * 0.35, 3)

    signals.sort(key=lambda x: x["_score"], reverse=True)
    return signals[:3]

# ── STEP 4: FIND CONTACT ──────────────────────────────────────────────────────

_BUYER_KW = [
    "vp engineering", "cto", "chief technology", "head of engineering",
    "head of ai", "ceo", "co-founder", "founder", "vp sales",
    "vp product", "director of engineering", "chief revenue"
]

async def _find_contact(company: dict, log: list) -> dict:
    domain        = company.get("domain", "")
    hunter_emails = company.get("hunter_emails", [])

    # T1: Hunter emails already fetched
    if hunter_emails:
        def rank(e: dict) -> tuple:
            pos  = (e.get("position") or "").lower()
            conf = e.get("confidence", 0)
            return (any(kw in pos for kw in _BUYER_KW), conf)

        best  = sorted(hunter_emails, key=rank, reverse=True)[0]
        email = best.get("value", "")
        if email:
            conf = best.get("confidence", 0)
            log.append(f"[Contact] Hunter T1: {email} | {best.get('position','')} | conf={conf}")
            return {
                "email":        email,
                "first_name":   best.get("first_name", ""),
                "last_name":    best.get("last_name", ""),
                "title":        best.get("position", ""),
                "email_status": "verified" if conf >= 80 else "likely",
                "source":       "hunter_t1"
            }

    # T2: Hunter verifier on pattern guesses
    if domain:
        for pattern in [f"hello@{domain}", f"info@{domain}", f"sales@{domain}"]:
            try:
                async with httpx.AsyncClient(timeout=8) as c:
                    r = await c.get(
                        "https://api.hunter.io/v2/email-verifier",
                        params={"email": pattern, "api_key": HUNTER_KEY}
                    )
                    r.raise_for_status()
                    if r.json().get("data", {}).get("result") == "deliverable":
                        log.append(f"[Contact] Hunter T2 verify: {pattern}")
                        return {
                            "email":        pattern,
                            "first_name":   "",
                            "last_name":    "",
                            "title":        "",
                            "email_status": "verified",
                            "source":       "hunter_verify_t2"
                        }
            except Exception:
                continue

    # T3: Pattern fallback
    if domain:
        guess = f"hello@{domain}"
        log.append(f"[Contact] Pattern T3: {guess}")
        return {
            "email":        guess,
            "first_name":   "",
            "last_name":    "",
            "title":        "",
            "email_status": "generic",
            "source":       "pattern_t3"
        }

    log.append("[Contact] No domain — cannot find contact")
    return {}

# ── STEP 5: GENERATE EMAIL + PPT ─────────────────────────────────────────────

async def _generate_email_and_ppt(
    company: dict,
    contact: dict,
    signals: list[dict],
    what_we_do: str,
    what_they_do: str,
    why_they_need_us: str,
    log: list
) -> tuple[str, str, str]:
    """Generate both email and personalized PPT"""
    
    # Generate email (same as before)
    subject, body = await _generate_email(
        company, contact, signals, what_we_do, what_they_do, why_they_need_us, log
    )
    
    # Generate personalized PPT
    try:
        from services.ppt_service import ppt_service
        
        icp_data = {
            "what_we_do": what_we_do,
            "what_they_do": what_they_do, 
            "why_they_need_us": why_they_need_us
        }
        
        ppt_path = await ppt_service.generate_personalized_ppt(
            company_data=company,
            contact_data=contact,
            signals=signals,
            icp_data=icp_data
        )
        
        log.append(f"[PPT] Generated personalized deck: {ppt_path}")
        return subject, body, ppt_path
        
    except Exception as e:
        log.append(f"[PPT] Generation failed: {e} — sending email only")
        return subject, body, ""

async def _generate_email(
    company: dict,
    contact: dict,
    signals: list[dict],
    what_we_do: str,
    what_they_do: str,
    why_they_need_us: str,
    log: list
) -> tuple[str, str]:
    signals_text = "\n".join([f"- {s['summary']}" for s in signals])
    fname        = contact.get("first_name", "there")

    system = f"""You write short, hyper-personalized B2B cold emails.
What our company does: {what_we_do}
Target company type:   {what_they_do}
Pain we solve:         {why_they_need_us}

Rules:
- Max 80 words in body
- Reference 1-2 signals naturally — do not list them
- No hype words in subject (Exciting, Amazing, Game-changer)
- End with exactly one question or CTA
- Sound like a human, not a tool"""

    user = f"""Company: {company.get('name')}
Industry: {company.get('industry', 'SaaS')}
Contact: {contact.get('first_name', '')} — {contact.get('title', '')}
Signals:
{signals_text}

Write: subject line then email body"""

    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={
                    "model":    "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user}
                    ],
                    "max_tokens":  300,
                    "temperature": 0.7
                }
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"]

        lines      = raw.strip().split("\n")
        subject    = ""
        body_lines = []
        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
            elif subject and line.strip():
                body_lines.extend(lines[i:])
                break
        body = "\n".join(body_lines).strip()
        if not subject:
            subject = lines[0]
            body    = "\n".join(lines[1:]).strip()

        log.append(f"[Email] Generated: '{subject}'")
        return subject, body

    except Exception as e:
        log.append(f"[Email] Groq failed: {e} — template fallback")
        sig = signals[0]["summary"] if signals else "your growth"
        return (
            f"Quick question for {company.get('name', '')}",
            f"Hi {fname},\n\nSaw {sig}. "
            f"Think we could help with {why_they_need_us.split(',')[0]}.\n\n"
            f"Worth a 15-min call?\n\nBest"
        )

# ── STEP 6: SEND WITH PPT ATTACHMENT ─────────────────────────────────────────

def _send_email_with_ppt(to: str, subject: str, body: str, ppt_path: str, log: list) -> bool:
    """Send email with personalized PPT attachment"""
    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to
        msg["List-Unsubscribe"] = f"<mailto:{SMTP_USER}?subject=unsubscribe>"
        
        # Add email body
        msg.attach(MIMEText(body, "plain"))
        
        # Add PPT attachment if generated
        if ppt_path and os.path.exists(ppt_path):
            from email.mime.application import MIMEApplication
            
            with open(ppt_path, "rb") as f:
                ppt_data = f.read()
            
            ppt_attachment = MIMEApplication(ppt_data, _subtype="vnd.openxmlformats-officedocument.presentationml.presentation")
            ppt_filename = os.path.basename(ppt_path)
            ppt_attachment.add_header("Content-Disposition", f"attachment; filename={ppt_filename}")
            msg.attach(ppt_attachment)
            
            log.append(f"[Send] Added PPT attachment: {ppt_filename}")
        
        # Send via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        
        attachment_note = " with personalized PPT" if ppt_path else ""
        log.append(f"[Send] Gmail SMTP{attachment_note} → {to}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        log.append("[Send] Auth failed — check SMTP_APP_PASSWORD")
        return False
    except Exception as e:
        log.append(f"[Send] Failed: {e}")
        return False

# ── SINGLE COMPANY PIPELINE ───────────────────────────────────────────────────

async def _process_one_company(
    company_name:     str,
    what_we_do:       str,
    what_they_do:     str,
    why_they_need_us: str,
    threshold:        int,
    good_funding:     list[str],
    icp_text:         str,
) -> OutreachResult:
    """Run the full pipeline for a single company. Returns OutreachResult."""
    log    = [f"Processing: {company_name}"]
    result = OutreachResult(company_name=company_name, icp_score=0, should_send=False)

    # Step 1: Enrich
    company = await _enrich_company(
        company_name, what_we_do, what_they_do, why_they_need_us, log
    )

    if not company.get("domain"):
        result.skip_reason = "Could not resolve domain"
        result.log         = log
        return result

    # Step 2: ICP score gate
    score, reason = _compute_icp_score(
        company, what_they_do, why_they_need_us,
        min_headcount=50, max_headcount=5000,
        good_funding=good_funding,
        threshold=threshold, log=log
    )
    result.icp_score = score

    if score < threshold:
        result.should_send = False
        result.skip_reason = f"ICP score {score} < threshold {threshold} ({reason})"
        result.log         = log
        return result

    result.should_send = True

    # Step 3: Signals
    signals            = await _harvest_signals(company, icp_text, log)
    result.top_signals = [s["summary"] for s in signals]

    # Step 4: Contact
    contact = await _find_contact(company, log)
    if not contact:
        result.skip_reason = "No contact email found"
        result.log         = log
        return result
    result.contact_email = contact.get("email")
    result.contact_name  = f"{contact.get('first_name','')} {contact.get('last_name','')}".strip()
    result.contact_title = contact.get("title", "")

    # Step 5: Email + PPT Generation
    subject, body, ppt_path = await _generate_email_and_ppt(
        company, contact, signals,
        what_we_do, what_they_do, why_they_need_us, log
    )
    result.email_subject = subject
    result.email_body    = body
    result.ppt_generated = bool(ppt_path)
    result.ppt_filename  = os.path.basename(ppt_path) if ppt_path else None

    # Step 6: Send with PPT attachment
    sent                = _send_email_with_ppt(contact["email"], subject, body, ppt_path, log)
    result.sent         = sent
    result.send_message = log[-1]
    result.log          = log
    return result

# ── MASTER FUNCTION ───────────────────────────────────────────────────────────

async def run_autonomous_outreach(
    what_we_do:       str,
    what_they_do:     str,
    why_they_need_us: str,
    max_companies:    int = 5,
) -> BatchOutreachResult:
    """
    PUBLIC FUNCTION. Called by FastAPI.
    Input:  3 ICP strings + max_companies int
    Output: BatchOutreachResult with all results + skipped list

    Flow:
      1. Discover company candidates from ICP using Serper
      2. Process each candidate in parallel (semaphore controlled)
      3. Collect results + skipped into BatchOutreachResult
    """
    batch_id = str(uuid.uuid4())[:8]
    icp_text = f"{what_we_do} {what_they_do} {why_they_need_us}"

    # Hard-coded ICP constraints (could be made configurable later)
    threshold    = int(os.getenv("ICP_THRESHOLD", "55"))
    good_funding = ["series_a", "series_b", "series_c"]

    # Step 0: Discover candidate companies
    # Discover more than needed — ICP gate will filter
    discover_count = max(max_companies * 3, 15)
    candidates = await discover_companies(
        what_we_do, what_they_do, why_they_need_us,
        target_count=discover_count
    )

    if not candidates:
        return BatchOutreachResult(
            batch_id             = batch_id,
            icp_summary          = what_they_do[:80],
            companies_discovered = 0,
            companies_scored     = 0,
            companies_passed_icp = 0,
            companies_contacted  = 0,
            results              = [],
            skipped              = [SkippedCompany(
                company_name="(all)",
                skip_reason="No companies discovered from ICP — check Serper API key"
            )]
        )

    # Process all candidates in parallel (max 3 at a time to respect rate limits)
    semaphore = asyncio.Semaphore(3)

    async def process_with_limit(name: str) -> OutreachResult:
        async with semaphore:
            return await _process_one_company(
                name, what_we_do, what_they_do, why_they_need_us,
                threshold, good_funding, icp_text
            )

    all_results = await asyncio.gather(
        *[process_with_limit(name) for name in candidates],
        return_exceptions=True
    )

    # Separate results into sent / skipped
    # Stop sending after max_companies successful sends
    results = []
    skipped = []
    sent_count = 0

    for r in all_results:
        # Handle unexpected exceptions from gather
        if isinstance(r, Exception):
            skipped.append(SkippedCompany(
                company_name="unknown",
                skip_reason=f"Unexpected error: {r}"
            ))
            continue

        if r.skip_reason:
            skipped.append(SkippedCompany(
                company_name=r.company_name,
                skip_reason=r.skip_reason
            ))
        elif r.sent and sent_count < max_companies:
            results.append(r)
            sent_count += 1
        elif r.should_send and not r.sent:
            # Passed ICP but send failed
            results.append(r)
        else:
            skipped.append(SkippedCompany(
                company_name=r.company_name,
                skip_reason=r.skip_reason or "max_companies limit reached"
            ))

    passed_icp = len([r for r in all_results
                      if not isinstance(r, Exception) and r.should_send])

    return BatchOutreachResult(
        batch_id             = batch_id,
        icp_summary          = what_they_do[:80],
        companies_discovered = len(candidates),
        companies_scored     = len(candidates),
        companies_passed_icp = passed_icp,
        companies_contacted  = sent_count,
        results              = results,
        skipped              = skipped
    )