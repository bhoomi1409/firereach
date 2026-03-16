"""
FireReach Orchestrator v2
User input: company_name (string) — NOTHING ELSE.
ICP config loads from .env — set once, never touched by user.
Hunter.io is T1 for company enrichment + contact finding.
"""

import os, re, math, asyncio, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from urllib.parse import urlparse
import httpx
from pydantic import BaseModel
from typing import Optional

# ── ICP FROM ENV ──────────────────────────────────────────────────────────────

class ICPConfig:
    what_we_do       = os.getenv("ICP_WHAT_WE_DO",        "We sell AI-powered outreach automation to B2B sales teams")
    what_they_do     = os.getenv("ICP_WHAT_THEY_DO",      "Series B SaaS companies with a sales or SDR team trying to grow pipeline")
    why_they_need_us = os.getenv("ICP_WHY_THEY_NEED_US",  "Low reply rates, hired new VP Sales, raised funding, expanding to new markets")
    min_headcount    = int(os.getenv("ICP_MIN_HC", "50"))
    max_headcount    = int(os.getenv("ICP_MAX_HC", "5000"))
    threshold        = int(os.getenv("ICP_THRESHOLD", "55"))
    good_funding     = ["series_a", "series_b", "series_c"]

ICP = ICPConfig()

# ── API KEYS ──────────────────────────────────────────────────────────────────

HUNTER_KEY  = os.getenv("HUNTER_API_KEY", "")
GROQ_KEY    = os.getenv("GROQ_API_KEY", "")
NEWSAPI_KEY = os.getenv("NEWS_API_KEY", "")
SERPER_KEY  = os.getenv("SERPER_API_KEY", "")
SMTP_USER   = os.getenv("SMTP_USER", "")
SMTP_PASS   = os.getenv("SMTP_APP_PASSWORD", "")

# ── RESPONSE MODEL ────────────────────────────────────────────────────────────

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
    sent:           bool = False
    send_message:   str = ""
    log:            list[str] = []

# ── SEMANTIC ENGINE (pure Python, no ML) ──────────────────────────────────────

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
    keys = set(va) | set(vb)
    dot = sum(va.get(k, 0) * vb.get(k, 0) for k in keys)
    ma = math.sqrt(sum(v * v for v in va.values()))
    mb = math.sqrt(sum(v * v for v in vb.values()))
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

# ── STEP 0: ENRICH COMPANY — Serper + Hunter ──────────────────────────────────

async def enrich_company(name: str, log: list) -> dict:
    """
    Source 1 — Serper: get domain from search results + description from snippets.
    Source 2 — Hunter domain-search: verify domain + store email list for Step 3.
    Returns dict with hunter_emails[] already populated — Step 3 uses this directly.
    """
    log.append(f"[Step 0] Enriching '{name}'...")
    result = {
        "name": name, "domain": "", "industry": "",
        "headcount": None, "funding": "", "description": "",
        "keywords": [], "technologies": [], "hunter_emails": []
    }

    # Source 1: Serper — extract domain + description
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": f"{name} company employees funding industry", "num": 5}
            )
            r.raise_for_status()
            organic = r.json().get("organic", [])
            snippets = [x.get("snippet", "") for x in organic]

            # Extract domain: find first URL whose netloc contains company name slug
            name_slug = re.sub(r'[^a-z0-9]', '', name.lower())[:6]
            for item in organic:
                netloc = urlparse(item.get("link", "")).netloc.replace("www.", "")
                if name_slug in netloc.replace(".", ""):
                    result["domain"] = netloc
                    break

            # Fallback domain guess if Serper didn't find it
            if not result["domain"]:
                result["domain"] = f"{re.sub(r'[^a-z0-9]', '', name.lower())}.com"

            result["description"] = " ".join(snippets[:2])
            result["keywords"] = _extract_keywords(snippets)
            log.append(f"[Step 0] Serper: domain={result['domain']} | {len(snippets)} snippets")
    except Exception as e:
        log.append(f"[Step 0] Serper failed: {e} — using guessed domain")
        result["domain"] = f"{re.sub(r'[^a-z0-9]', '', name.lower())}.com"

    # Source 2: Hunter domain-search — get emails + confirm org name
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(
                "https://api.hunter.io/v2/domain-search",
                params={
                    "domain": result["domain"],
                    "api_key": HUNTER_KEY,
                    "limit": 10,
                    "type": "personal"
                }
            )
            r.raise_for_status()
            data = r.json().get("data", {})
            result["name"] = data.get("organization") or name
            result["hunter_emails"] = data.get("emails", [])
            log.append(f"[Step 0] Hunter: {len(result['hunter_emails'])} emails found at {result['domain']}")
    except Exception as e:
        log.append(f"[Step 0] Hunter domain-search failed: {e}")

    return result

# ── STEP 1: ICP SCORING ───────────────────────────────────────────────────────

def compute_icp_score(company: dict, log: list) -> tuple[float, str]:
    corpus = " ".join([
        company.get("description", ""),
        company.get("industry", ""),
        " ".join(company.get("keywords", [])),
        " ".join(company.get("technologies", [])),
    ])

    fit_sim  = _sim(ICP.what_they_do,     corpus)   # 40 pts
    pain_sim = _sim(ICP.why_they_need_us, corpus)   # 40 pts

    # Structural: headcount + funding (20 pts)
    struct = 0
    hc = company.get("headcount") or 0
    if ICP.min_headcount <= hc <= ICP.max_headcount:
        struct += 12
    elif hc > 0:
        struct += 4
    fs = (company.get("funding", "")).lower().replace(" ", "_")
    if fs in ICP.good_funding:
        struct += 8
    elif fs in ["seed", "series_d"]:
        struct += 4

    total = round(min(100, fit_sim * 40 + pain_sim * 40 + struct), 1)
    reason = f"fit={fit_sim:.0%} pain={pain_sim:.0%} struct={struct}/20"
    log.append(f"[Step 1] ICP score: {total} ({reason})")
    return total, reason

# ── STEP 2: SIGNAL HARVEST + RERANK ──────────────────────────────────────────

async def harvest_signals(company: dict, log: list) -> list[dict]:
    name    = company.get("name", "")
    signals = []

    # News via NewsAPI
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(
                "https://newsapi.org/v2/everything",
                params={"q": name, "sortBy": "publishedAt",
                        "pageSize": 3, "apiKey": NEWSAPI_KEY}
            )
            for a in r.json().get("articles", []):
                signals.append({
                    "type": "news",
                    "summary": a.get("title", ""),
                    "detected_at": a.get("publishedAt", datetime.utcnow().isoformat())
                })
        log.append(f"[Step 2] News: {len([s for s in signals if s['type']=='news'])} articles")
    except Exception as e:
        log.append(f"[Step 2] NewsAPI failed: {e}")

    # Web signals via Serper
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": f"{name} funding OR expansion OR launch 2025", "num": 3}
            )
            for item in r.json().get("organic", []):
                signals.append({
                    "type": "web",
                    "summary": item.get("snippet", ""),
                    "detected_at": datetime.utcnow().isoformat()
                })
        log.append("[Step 2] Web signals: fetched")
    except Exception as e:
        log.append(f"[Step 2] Serper web failed: {e}")

    # Job signals via Serper (hiring data)
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
                json={"q": f'"{name}" "is hiring" engineer OR developer OR AI', "num": 5}
            )
            for item in r.json().get("organic", []):
                snippet = item.get("snippet", "")
                # Skip generic job boards — only keep company domain + linkedin
                link = item.get("link", "")
                if any(bd in link for bd in ["indeed.com", "glassdoor.com", "ziprecruiter"]):
                    continue
                if len(snippet) > 40:
                    signals.append({
                        "type": "hiring",
                        "summary": f"Hiring signal: {snippet[:100]}",
                        "detected_at": datetime.utcnow().isoformat()
                    })
        log.append("[Step 2] Serper jobs: fetched")
    except Exception as e:
        log.append(f"[Step 2] Serper jobs failed: {e}")

    # Rerank: type_weight × 0.30 + freshness × 0.35 + icp_relevance × 0.35
    icp_text = f"{ICP.what_we_do} {ICP.what_they_do} {ICP.why_they_need_us}"
    TYPE_W   = {"funding": 1.0, "exec_hire": 0.9, "hiring": 0.8, "news": 0.6, "web": 0.5}

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
    top3 = signals[:3]
    log.append(f"[Step 2] Reranked — top: {top3[0]['summary'][:60] if top3 else 'none'}")
    return top3

# ── STEP 3: FIND CONTACT — Hunter T1/T2/T3, Generic T4 ───────────────────────

_BUYER_KEYWORDS = [
    "vp engineering", "cto", "chief technology", "head of engineering",
    "head of ai", "ceo", "co-founder", "founder", "vp sales",
    "vp product", "director of engineering", "chief revenue"
]

async def find_contact(company: dict, log: list) -> dict:
    """
    T1 — Hunter domain-search results (already in company dict from Step 0).
         Sort by buyer title match + confidence. Pick best.
    T2 — Hunter email-verifier on role-pattern guesses.
         Try hello@, info@, sales@ — use first that is "deliverable".
    T3 — Pattern guess, no verification.
    T4 — Generic role prefix, always succeeds.
    """
    domain        = company.get("domain", "")
    hunter_emails = company.get("hunter_emails", [])   # populated in Step 0

    # T1: pick best from Hunter emails already fetched
    if hunter_emails:
        def rank(e: dict) -> tuple:
            pos  = (e.get("position") or "").lower()
            conf = e.get("confidence", 0)
            return (any(kw in pos for kw in _BUYER_KEYWORDS), conf)

        best = sorted(hunter_emails, key=rank, reverse=True)[0]
        email = best.get("value", "")
        if email:
            conf = best.get("confidence", 0)
            log.append(f"[Step 3] Hunter T1: {email} | {best.get('position','')} | conf={conf}")
            return {
                "email":        email,
                "first_name":   best.get("first_name", ""),
                "last_name":    best.get("last_name", ""),
                "title":        best.get("position", ""),
                "email_status": "verified" if conf >= 80 else "likely",
                "source":       "hunter_domain_t1"
            }

    # T2: Hunter email-verifier on pattern guesses
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
                        log.append(f"[Step 3] Hunter T2 verify: {pattern} deliverable")
                        return {
                            "email": pattern, "first_name": "", "last_name": "",
                            "title": "", "email_status": "verified",
                            "source": "hunter_verify_t2"
                        }
            except Exception:
                continue

    # T3: Pattern guess (no verification)
    if domain:
        guess = f"hello@{domain}"
        log.append(f"[Step 3] Pattern T3: {guess}")
        return {
            "email": guess, "first_name": "", "last_name": "",
            "title": "", "email_status": "generic", "source": "pattern_t3"
        }

    log.append("[Step 3] No contact found — no domain")
    return {}

# ── STEP 4: GENERATE EMAIL via Groq ──────────────────────────────────────────

async def generate_email(
    company: dict, contact: dict, signals: list[dict], log: list
) -> tuple[str, str]:
    signals_text = "\n".join([f"- {s['summary']}" for s in signals])
    fname        = contact.get("first_name", "there")

    system = f"""You write short, hyper-personalized B2B cold emails.
What our company does: {ICP.what_we_do}
Target company type:   {ICP.what_they_do}
Pain we solve:         {ICP.why_they_need_us}

Rules:
- Max 80 words in body
- Reference 1-2 signals naturally — do not list them
- No hype words in subject (Exciting, Amazing, Game-changer)
- End with one clear question or CTA
- Sound human, not automated"""

    user = f"""Company: {company.get('name')}
Industry: {company.get('industry')}
Contact: {contact.get('first_name', '')} — {contact.get('title', '')}
Recent signals:
{signals_text}

Write: subject line + email body"""

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

        lines   = raw.strip().split("\n")
        subject = ""
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

        log.append(f"[Step 4] Email generated: '{subject}'")
        return subject, body

    except Exception as e:
        log.append(f"[Step 4] Groq failed: {e} — using template")
        sig = signals[0]["summary"] if signals else "your recent growth"
        return (
            f"Quick question for {company.get('name', '')}",
            f"Hi {fname},\n\nSaw {sig}. "
            f"Given what you're building, I think we could help with "
            f"{ICP.why_they_need_us.split(',')[0]}.\n\n"
            f"Worth a 15-min call this week?\n\nBest"
        )

# ── STEP 5: SEND via Gmail SMTP ───────────────────────────────────────────────

def send_email(to: str, subject: str, body: str, log: list) -> bool:
    try:
        msg = MIMEMultipart()
        msg["Subject"]          = subject
        msg["From"]             = SMTP_USER
        msg["To"]               = to
        msg["List-Unsubscribe"] = f"<mailto:{SMTP_USER}?subject=unsubscribe>"
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        log.append(f"[Step 5] Sent via Gmail SMTP → {to}")
        return True
    except smtplib.SMTPAuthenticationError:
        log.append("[Step 5] Gmail auth failed — check SMTP_APP_PASSWORD")
        return False
    except Exception as e:
        log.append(f"[Step 5] Send failed: {e}")
        return False

# ── MASTER FUNCTION ───────────────────────────────────────────────────────────

async def run_outreach(company_name: str) -> OutreachResult:
    """Only public function. Input: company_name string. Output: OutreachResult."""
    log    = [f"Starting outreach for: {company_name}"]
    result = OutreachResult(company_name=company_name, icp_score=0, should_send=False)

    # Step 0: Enrich — Serper + Hunter
    company = await enrich_company(company_name, log)
    if not company.get("domain"):
        result.skip_reason = "Could not resolve company domain"
        result.log = log
        return result

    # Step 1: ICP gate
    score, reason = compute_icp_score(company, log)
    result.icp_score = score
    if score < ICP.threshold:
        result.should_send = False
        result.skip_reason = f"ICP score {score} < threshold {ICP.threshold} ({reason})"
        result.log = log
        log.append(f"SKIPPED — {result.skip_reason}")
        return result

    result.should_send = True

    # Step 2: Signals
    signals = await harvest_signals(company, log)
    result.top_signals = [s["summary"] for s in signals]

    # Step 3: Contact
    contact = await find_contact(company, log)
    if not contact:
        result.skip_reason = "No contact email found"
        result.log = log
        return result
    result.contact_email = contact.get("email")
    result.contact_name  = f"{contact.get('first_name','')} {contact.get('last_name','')}".strip()
    result.contact_title = contact.get("title", "")

    # Step 4: Generate email
    subject, body       = await generate_email(company, contact, signals, log)
    result.email_subject = subject
    result.email_body    = body

    # Step 5: Send
    sent                = send_email(contact["email"], subject, body, log)
    result.sent         = sent
    result.send_message = log[-1]
    result.log          = log
    return result