"""
FireReach v4 — All Pydantic models.
"""

from pydantic import BaseModel
from typing import Optional

class ParsedICP(BaseModel):
    what_we_do:       str
    target_industry:  str
    target_stage:     str
    pain_keyword:     str
    solution_keyword: str
    buyer_titles:     list[str]
    min_headcount:    int = 50
    max_headcount:    int = 5000
    threshold:        int = 25  # Temporarily lowered for testing

class DiscoveredCompany(BaseModel):
    name:     str
    domain:   str = ""
    reason:   str = ""
    approved: bool = True           # checkbox state
    is_demo:  bool = False          # true if fallback demo company

class DiscoverResponse(BaseModel):
    session_id: str
    icp_parsed: ParsedICP
    companies:  list[DiscoveredCompany]

class Signal(BaseModel):
    signal_id:     str              # sha256 of summary — dedup key
    type:          str              # S1-S7 type string
    summary:       str
    detected_at:   str
    type_weight:   float
    freshness:     float
    icp_relevance: float
    final_score:   float

class ContactResult(BaseModel):
    email:        str
    first_name:   str = ""
    last_name:    str = ""
    title:        str = ""
    email_status: str = "generic"   # verified|likely|generic
    source:       str = ""
    confidence:   int = 0

class GeneratedContent(BaseModel):
    email_subject:  str
    email_body:     str
    brochure_html:  str

class CompanyResult(BaseModel):
    company_name:    str
    domain:          str = ""
    icp_score:       float
    should_send:     bool
    skip_reason:     Optional[str] = None
    signals_used:    list[Signal] = []
    contact:         Optional[ContactResult] = None
    email_subject:   Optional[str] = None
    email_body:      Optional[str] = None
    brochure_html:   Optional[str] = None
    sent:            bool = False
    send_message:    str = ""
    log:             list[str] = []

class SkippedCompany(BaseModel):
    company_name: str
    skip_reason:  str

class BatchResult(BaseModel):
    batch_id:             str
    session_id:           str
    icp_summary:          str
    companies_discovered: int
    companies_approved:   int
    companies_scored:     int
    companies_passed_icp: int
    emails_sent:          int
    results:              list[CompanyResult] = []
    skipped:              list[SkippedCompany] = []

class FollowUpDraft(BaseModel):
    company_name:    str
    trigger_signal:  Signal
    draft_subject:   str
    draft_body:      str
    scheduled_at:    str            # ISO datetime
    status:          str = "pending" # pending|approved|sent|skipped