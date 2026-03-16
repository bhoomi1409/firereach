"""
FireReach — Session Store (In-Memory for Demo)
Stores: session_id → {icp_parsed, companies[], created_at}
TTL: 30 minutes (1800 seconds)
"""

import json
import uuid
import time
from models import ParsedICP, DiscoveredCompany

# In-memory store for demo
_sessions = {}

async def create_session(icp: ParsedICP, companies: list[DiscoveredCompany]) -> str:
    """Create new session, return session_id."""
    sid = str(uuid.uuid4())[:12]
    payload = {
        "icp":       icp.model_dump(),
        "companies": [c.model_dump() for c in companies],
        "created_at": time.time()
    }
    _sessions[sid] = payload
    return sid

async def get_session(sid: str) -> dict | None:
    if sid not in _sessions:
        return None
    
    # Check TTL (30 minutes)
    session = _sessions[sid]
    if time.time() - session["created_at"] > 1800:
        del _sessions[sid]
        return None
    
    return session

async def update_companies(sid: str, approved_names: list[str]) -> bool:
    """Mark companies as approved/unapproved based on user checkbox state."""
    data = await get_session(sid)
    if not data:
        return False
    approved_set = set(n.lower() for n in approved_names)
    for c in data["companies"]:
        c["approved"] = c["name"].lower() in approved_set
    # Update timestamp
    data["created_at"] = time.time()
    return True

async def get_approved_companies(sid: str) -> tuple[ParsedICP | None, list[DiscoveredCompany]]:
    data = await get_session(sid)
    if not data:
        return None, []
    icp       = ParsedICP(**data["icp"])
    companies = [DiscoveredCompany(**c) for c in data["companies"] if c.get("approved", True)]
    return icp, companies

async def set_session_status(sid: str, status_data: dict) -> bool:
    """Set session status (running, completed, failed)."""
    data = await get_session(sid)
    if not data:
        return False
    data["status"] = status_data
    data["created_at"] = time.time()  # Update timestamp
    return True

async def get_session_status(sid: str) -> dict | None:
    """Get session status."""
    data = await get_session(sid)
    if not data:
        return None
    return data.get("status")