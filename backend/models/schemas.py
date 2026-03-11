from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class OutreachRequest(BaseModel):
    icp: str                          # e.g. "We sell cybersecurity training to Series B startups"
    target_company: str               # e.g. "Stripe"
    recipient_email: str              # Where to send the outreach email
    sender_name: str = "Alex"         # Name to sign the email with

class SignalData(BaseModel):
    funding_rounds: Optional[str] = None
    leadership_changes: Optional[str] = None
    hiring_trends: Optional[List[str]] = []
    tech_stack_changes: Optional[str] = None
    news_mentions: Optional[List[str]] = []
    g2_signals: Optional[str] = None
    headcount_growth: Optional[str] = None
    raw_signal_count: int = 0

class OutreachResponse(BaseModel):
    success: bool
    signals: SignalData
    account_brief: str
    email_subject: str
    email_body: str
    send_status: bool
    send_message: str
    execution_log: List[str]
    error: Optional[str] = None