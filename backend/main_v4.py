"""
FireReach v4 — Three endpoints:
  POST /api/discover → parse ICP + find companies → return list with checkboxes
  PATCH /api/session/{id}/companies → update approved companies (checkbox state)
  POST /api/run → run full pipeline on approved companies
  GET  /health
"""

import asyncio
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from models import (DiscoverResponse, BatchResult, CompanyResult,
                    SkippedCompany, ParsedICP)
from icp_parser import parse_icp
from session_store import create_session, get_approved_companies, update_companies
from dedup_store import already_sent, record_sent, get_used_signals

app = FastAPI(title="FireReach", version="4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

SMTP_USER = __import__("os").getenv("SMTP_USER", "")

# ── REQUEST MODELS ────────────────────────────────────────────────────────────

class DiscoverRequest(BaseModel):
    icp_text:      str
    target_count:  Optional[int] = 10

class UpdateCompaniesRequest(BaseModel):
    approved_names: list[str]   # names of companies user kept checked

class RunRequest(BaseModel):
    session_id: str
    max_send:   Optional[int] = 5

# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "4.0"}

@app.post("/api/discover", response_model=DiscoverResponse)
async def discover(req: DiscoverRequest):
    if not req.icp_text.strip() or len(req.icp_text.strip()) < 20:
        raise HTTPException(400, "icp_text must be at least 20 characters. Describe your service and ideal customer.")

    target = min(max(1, req.target_count or 10), 20)

    # Parse ICP from free text
    icp = await parse_icp(req.icp_text)

    # Discover companies using parsed ICP
    from company_discovery_v4 import discover_companies
    companies = await discover_companies(icp, target_count=target * 2)

    if not companies:
        raise HTTPException(422, "Could not discover any companies from your ICP description. Try being more specific about the industry or company type.")

    # Store in session
    session_id = await create_session(icp, companies)

    return DiscoverResponse(
        session_id = session_id,
        icp_parsed = icp,
        companies  = companies[:target],
    )
@app.patch("/api/session/{session_id}/companies")
async def update_company_selection(session_id: str, req: UpdateCompaniesRequest):
    """Called by frontend when user checks/unchecks companies."""
    ok = await update_companies(session_id, req.approved_names)
    if not ok:
        raise HTTPException(404, "Session not found or expired (30 min TTL). Please run discovery again.")
    return {"status": "updated", "approved_count": len(req.approved_names)}

@app.post("/api/run", response_model=BatchResult)
async def run_outreach(req: RunRequest):
    max_send = min(max(1, req.max_send or 5), 20)

    # Get approved companies from session
    icp, companies = await get_approved_companies(req.session_id)
    if icp is None:
        raise HTTPException(404, "Session not found or expired. Please run discovery again.")
    if not companies:
        raise HTTPException(400, "No companies approved. Please select at least one company.")

    batch_id = str(uuid.uuid4())[:8]
    sem      = asyncio.Semaphore(3)

    async def process(company_name: str, domain_hint: str) -> CompanyResult:
        async with sem:
            log    = [f"Processing: {company_name}"]
            result = CompanyResult(company_name=company_name,
                                   domain=domain_hint, icp_score=0, should_send=False)

            # Step 1: Enrich
            from enrichment_v4 import enrich_company
            company = await enrich_company(company_name, domain_hint)
            result.domain = company.get("domain", domain_hint)

            # Step 2: Dedup check
            domain = company.get("domain", "")
            if domain and already_sent(domain, SMTP_USER, days=90):
                result.skip_reason = "Already contacted within 90 days"
                result.log = log
                return result

            # Step 3: ICP score
            from icp_scorer_v4 import score_company
            score, reason, proceed = score_company(company, icp)
            result.icp_score = score
            log.append(f"[Score] {score} ({reason})")
            if not proceed:
                result.skip_reason = f"ICP score {score} < threshold {icp.threshold} ({reason})"
                result.log = log
                return result

            result.should_send = True

            # Step 4: Signals (exclude already-used signals if re-run)
            from signal_engine_v4 import extract_signals
            used_ids = get_used_signals(domain, SMTP_USER)
            signals  = extract_signals(company, icp)
            # Filter out previously used signal IDs
            fresh_signals = [s for s in signals if s.signal_id not in used_ids]
            if not fresh_signals:
                fresh_signals = signals   # use all if everything was used before
            result.signals_used = fresh_signals[:3]
            log.append(f"[Signals] Top: {fresh_signals[0].summary[:60] if fresh_signals else 'none'}")

            # Step 5: Contact
            from contact_finder_v4 import find_contact
            contact = await find_contact(company, icp.buyer_titles)
            if not contact.email:
                result.skip_reason = "No contact email found"
                result.log = log
                return result
            result.contact = contact
            log.append(f"[Contact] {contact.email} ({contact.source})")

            # Step 6: Generate email + brochure (ONE Groq call)
            from content_generator_v4 import generate_content
            content = await generate_content(
                company, contact.model_dump(), fresh_signals[:3], icp
            )
            result.email_subject = content.email_subject
            result.email_body    = content.email_body
            result.brochure_html = content.brochure_html
            log.append(f"[Content] Subject: {content.email_subject}")

            # Step 7: Send
            from email_sender_v4 import send_with_brochure
            sent = send_with_brochure(
                contact.email, content.email_subject,
                content.email_body, content.brochure_html,
                company_name, log
            )
            result.sent = sent

            # Step 8: Record send (dedup + signal tracking)
            if sent:
                record_sent(domain, SMTP_USER,
                            [s.signal_id for s in fresh_signals[:3]])

            result.send_message = log[-1]
            result.log          = log
            return result

    # Run all
    all_results = await asyncio.gather(
        *[process(c.name, c.domain) for c in companies],
        return_exceptions=True
    )

    results  = []
    skipped  = []
    sent_cnt = 0

    for r in all_results:
        if isinstance(r, Exception):
            skipped.append(SkippedCompany(company_name="unknown", skip_reason=str(r)))
            continue
        if r.skip_reason:
            skipped.append(SkippedCompany(company_name=r.company_name, skip_reason=r.skip_reason))
        elif r.sent and sent_cnt < max_send:
            results.append(r)
            sent_cnt += 1
        elif r.should_send and not r.sent:
            results.append(r)   # include failed sends in results
        else:
            skipped.append(SkippedCompany(
                company_name=r.company_name,
                skip_reason=r.skip_reason or "max_send limit reached"
            ))

    passed = len([r for r in all_results
                  if not isinstance(r, Exception) and r.should_send])

    return BatchResult(
        batch_id             = batch_id,
        session_id           = req.session_id,
        icp_summary          = icp.what_we_do[:80],
        companies_discovered = len(companies),
        companies_approved   = len(companies),
        companies_scored     = len(companies),
        companies_passed_icp = passed,
        emails_sent          = sent_cnt,
        results              = results,
        skipped              = skipped,
    )