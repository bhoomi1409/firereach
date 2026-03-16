"""
FireReach — Follow-up Engine
Signal-triggered follow-ups with signal diff detection
"""

import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List
from models import Signal, FollowUpDraft, ParsedICP, ContactResult
from dedup_store import get_used_signals
from signal_engine_v4 import extract_signals
from content_generator_v4 import generate_content

async def detect_new_signals(domain: str, sender: str, company: dict, icp: ParsedICP) -> List[Signal]:
    """
    Extract current signals and compare with previously used ones.
    Returns only new signals that weren't used in previous outreach.
    """
    # Get all current signals
    current_signals = extract_signals(company, icp)
    
    # Get previously used signal IDs
    used_signal_ids = set(get_used_signals(domain, sender))
    
    # Filter to only new signals
    new_signals = [s for s in current_signals if s.signal_id not in used_signal_ids]
    
    # Sort by relevance and freshness
    new_signals.sort(key=lambda s: s.final_score, reverse=True)
    
    return new_signals

async def generate_followup_draft(
    company: dict,
    contact: ContactResult,
    trigger_signal: Signal,
    icp: ParsedICP,
    previous_subject: str = ""
) -> FollowUpDraft:
    """
    Generate a follow-up email draft based on a new trigger signal.
    """
    company_name = company.get('name', 'Company')
    
    # Create follow-up specific prompt
    followup_prompt = f"""Generate a professional follow-up email for:

Company: {company_name}
Contact: {contact.first_name} {contact.last_name}
Previous Subject: {previous_subject}
New Trigger Signal: {trigger_signal.summary}
Our Service: {icp.what_we_do}

This is a follow-up to a previous outreach. Reference the new signal naturally and provide additional value. Keep it brief and professional."""

    try:
        # Use existing content generator but with follow-up context
        content = await generate_content(
            company, contact.model_dump(), [trigger_signal], icp
        )
        
        # Create follow-up draft
        draft = FollowUpDraft(
            company_name=company_name,
            trigger_signal=trigger_signal,
            draft_subject=f"Re: {previous_subject}" if previous_subject else content.email_subject,
            draft_body=content.email_body,
            scheduled_at=(datetime.utcnow() + timedelta(days=7)).isoformat(),
            status="pending"
        )
        
        return draft
        
    except Exception as e:
        # Fallback draft
        return FollowUpDraft(
            company_name=company_name,
            trigger_signal=trigger_signal,
            draft_subject=f"Follow-up: {trigger_signal.type} update at {company_name}",
            draft_body=f"""Hi {contact.first_name},

I wanted to follow up on my previous message regarding {icp.what_we_do}.

I noticed {trigger_signal.summary} and thought this might be relevant to our previous conversation about {icp.pain_keyword}.

Would you be interested in a brief 15-minute call to discuss how this development might impact your current priorities?

Best regards,
[Your Name]""",
            scheduled_at=(datetime.utcnow() + timedelta(days=7)).isoformat(),
            status="pending"
        )

async def scan_for_followups(batch_companies: List[dict], icp: ParsedICP, sender: str) -> List[FollowUpDraft]:
    """
    Scan a batch of companies for new signals that could trigger follow-ups.
    """
    followup_drafts = []
    
    for company in batch_companies:
        domain = company.get('domain', '')
        if not domain:
            continue
            
        # Detect new signals
        new_signals = await detect_new_signals(domain, sender, company, icp)
        
        if new_signals:
            # Get the strongest new signal
            trigger_signal = new_signals[0]
            
            # Create a basic contact (would normally come from previous outreach data)
            contact = ContactResult(
                email=f"contact@{domain}",
                first_name="there",
                last_name="",
                title="",
                email_status="generic",
                source="followup_scan"
            )
            
            # Generate follow-up draft
            draft = await generate_followup_draft(
                company, contact, trigger_signal, icp
            )
            
            followup_drafts.append(draft)
    
    return followup_drafts

def calculate_signal_diff(old_signals: List[Signal], new_signals: List[Signal]) -> dict:
    """
    Calculate the difference between old and new signal sets.
    Returns summary of what's new, changed, or disappeared.
    """
    old_ids = {s.signal_id for s in old_signals}
    new_ids = {s.signal_id for s in new_signals}
    
    added = [s for s in new_signals if s.signal_id not in old_ids]
    removed = [s for s in old_signals if s.signal_id not in new_ids]
    
    # Check for score changes in existing signals
    old_scores = {s.signal_id: s.final_score for s in old_signals}
    changed = []
    for signal in new_signals:
        if signal.signal_id in old_scores:
            old_score = old_scores[signal.signal_id]
            if abs(signal.final_score - old_score) > 0.1:  # Significant change
                changed.append({
                    'signal': signal,
                    'old_score': old_score,
                    'new_score': signal.final_score,
                    'change': signal.final_score - old_score
                })
    
    return {
        'added': added,
        'removed': removed,
        'changed': changed,
        'summary': f"{len(added)} new, {len(removed)} removed, {len(changed)} changed"
    }