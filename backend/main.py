"""
FireReach v4 — Three endpoints:
  POST /api/discover → parse ICP + find companies → return list with checkboxes
  PATCH /api/session/{id}/companies → update approved companies (checkbox state)
  POST /api/run → run full pipeline on approved companies
  GET  /health
"""

import asyncio
import uuid
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

# Load environment variables
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent

# Try multiple paths for .env file
env_paths = [
    script_dir / '.env',  # Same directory as this file
    script_dir.parent / '.env',  # Parent directory
    '.env',  # Current working directory
]

print(f"DEBUG: Script directory: {script_dir}")
for env_path in env_paths:
    print(f"DEBUG: Trying .env path: {env_path}")
    if Path(env_path).exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            print(f"DEBUG: Successfully loaded .env from {env_path}")
            break
        except ImportError:
            # Fallback: load .env manually
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
                print(f"DEBUG: Manually loaded .env from {env_path}")
                break
            except Exception as e:
                print(f"DEBUG: Failed to load {env_path}: {e}")
                continue
    else:
        print(f"DEBUG: .env file not found at {env_path}")

# Verify key loading
print(f"DEBUG: GROQ_API_KEY length: {len(os.getenv('GROQ_API_KEY', ''))}")
print(f"DEBUG: SERP_API_KEY length: {len(os.getenv('SERP_API_KEY', ''))}")

from models import (DiscoverResponse, BatchResult, CompanyResult,
                    SkippedCompany, ParsedICP)
from icp_parser import parse_icp
from session_store import create_session, get_approved_companies, update_companies, set_session_status, get_session_status
from followup_engine import scan_for_followups, generate_followup_draft
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

@app.get("/api/status/{session_id}")
async def get_session_status_endpoint(session_id: str):
    """Get current session status - running, completed, or not found."""
    status = await get_session_status(session_id)
    if not status:
        raise HTTPException(404, "Session not found or expired")
    return status

@app.get("/api/run/stream/{session_id}")
async def stream_outreach_progress(session_id: str):
    """Stream real-time progress updates via Server-Sent Events."""
    async def event_generator():
        # Check if session exists
        icp, companies = await get_approved_companies(session_id)
        if icp is None:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return
            
        total_companies = len(companies)
        
        for i, company in enumerate(companies):
            progress = {
                'step': f'processing_company_{i+1}',
                'company': company.name,
                'progress': round((i / total_companies) * 100),
                'message': f'Processing {company.name} ({i+1}/{total_companies})'
            }
            yield f"data: {json.dumps(progress)}\n\n"
            await asyncio.sleep(0.5)  # Simulate processing time
            
        # Final completion
        yield f"data: {json.dumps({'step': 'completed', 'progress': 100, 'message': 'All companies processed'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/api/followups/{batch_id}")
async def get_followup_drafts(batch_id: str):
    """Get follow-up drafts for a completed batch."""
    # This would normally query stored batch results
    # For now, return empty list as placeholder
    return {"followups": [], "batch_id": batch_id}

@app.post("/api/followups/{draft_id}/approve")
async def approve_followup(draft_id: str):
    """Approve and send a follow-up draft."""
    # This would normally retrieve the draft, send the email, and update status
    return {"status": "approved", "draft_id": draft_id, "sent": True}

@app.post("/api/discover", response_model=DiscoverResponse)
async def discover(req: DiscoverRequest):
    if not req.icp_text.strip() or len(req.icp_text.strip()) < 20:
        raise HTTPException(400, "icp_text must be at least 20 characters. Describe your service and ideal customer.")

    target = min(max(1, req.target_count or 10), 20)

    # Parse ICP from free text
    print(f"DEBUG: Parsing ICP text: {req.icp_text[:100]}...")
    icp = await parse_icp(req.icp_text)
    print(f"DEBUG: Parsed ICP - industry: {icp.target_industry}, stage: {icp.target_stage}")

    # Discover companies using parsed ICP
    from company_discovery_v4 import discover_companies
    print(f"DEBUG: Calling discover_companies with industry: {icp.target_industry}")
    companies = await discover_companies(icp, target_count=target)
    print(f"DEBUG: Discovered {len(companies)} companies, first few demo flags: {[c.is_demo for c in companies[:3]]}")

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
    # Validate and clamp max_send
    if req.max_send is not None and req.max_send <= 0:
        raise HTTPException(400, "max_send must be greater than 0")
    max_send = min(max(1, req.max_send or 5), 20)

    # Check if session is already running (prevent double-click)
    current_status = await get_session_status(req.session_id)
    if current_status and current_status.get("status") == "running":
        raise HTTPException(409, "Outreach already in progress for this session")

    # Get approved companies from session
    icp, companies = await get_approved_companies(req.session_id)
    if icp is None:
        raise HTTPException(404, "Session not found or expired. Please run discovery again.")
    if not companies:
        raise HTTPException(400, "No companies approved. Please select at least one company.")

    # Set session status to running
    batch_id = str(uuid.uuid4())[:8]
    await set_session_status(req.session_id, {"status": "running", "batch_id": batch_id})

    try:
        sem      = asyncio.Semaphore(3)
        groq_sem = asyncio.Semaphore(1)  # Serial Groq calls to avoid rate limits

        async def process(company_name: str, domain_hint: str) -> CompanyResult:
            async with sem:
                log    = [f"Processing: {company_name}"]
                result = CompanyResult(company_name=company_name,
                                       domain=domain_hint, icp_score=0, should_send=False)
            
                try:
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
                    if not contact or not contact.email or not contact.email.strip():
                        result.skip_reason = "No contact email found"
                        result.log = log
                        return result
                    result.contact = contact
                    log.append(f"[Contact] {contact.email} ({contact.source})")

                    # Step 6: Generate email + brochure (ONE Groq call)
                    from content_generator_v4 import generate_content
                    async with groq_sem:  # Serialize Groq calls to avoid rate limits
                        await asyncio.sleep(0.5)  # Small delay between Groq calls
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
                    
                except Exception as e:
                    # Catch any uncaught exceptions to prevent "unknown" company names
                    result.skip_reason = f"Processing error: {str(e)}"
                    result.log = log + [f"[Error] {str(e)}"]
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

        result = BatchResult(
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
        
        # Mark session as completed and store result
        await set_session_status(req.session_id, {
            "status": "completed", 
            "batch_id": batch_id,
            "result": result.model_dump()
        })
        
        return result

    except Exception as e:
        # Mark session as failed on any error
        await set_session_status(req.session_id, {
            "status": "failed", 
            "batch_id": batch_id,
            "error": str(e)
        })
        raise