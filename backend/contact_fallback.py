"""
FireReach — Contact Enrichment (Hunter.io only)
T1: Hunter domain-search — sort emails by buyer title + confidence
T2: Hunter email-finder  — find specific person by name + domain
T3: Hunter email-verifier — check if pattern guess is deliverable
T4: Generic role prefix  — always succeeds, no API needed
"""

import os
import httpx
from typing import Optional
from pydantic import BaseModel
from fallback_engine import try_with_circuit

HUNTER_KEY = os.getenv("HUNTER_API_KEY", "")

_BUYER_KEYWORDS = [
    "vp engineering", "cto", "chief technology", "head of engineering",
    "head of ai", "ceo", "co-founder", "founder", "vp sales",
    "vp product", "director of engineering", "chief revenue officer"
]

class ContactResult(BaseModel):
    email:        str
    email_status: str              # "verified" | "likely" | "guessed" | "generic"
    first_name:   Optional[str] = None
    last_name:    Optional[str] = None
    title:        Optional[str] = None
    linkedin_url: Optional[str] = None
    confidence:   int = 0          # Hunter confidence score 0-100
    source:       str = ""         # which tier found this

# ── T1: Hunter domain-search ──────────────────────────────────────────────────

async def _hunter_domain_search(domain: str) -> Optional[ContactResult]:
    """
    Fetch all emails at domain. Sort by buyer title match then confidence.
    Returns best match or None if no emails found.
    """
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": HUNTER_KEY,
                    "limit": 10, "type": "personal"}
        )
        r.raise_for_status()
        emails = r.json().get("data", {}).get("emails", [])
        if not emails:
            return None

        def rank(e: dict) -> tuple:
            pos  = (e.get("position") or "").lower()
            conf = e.get("confidence", 0)
            return (any(kw in pos for kw in _BUYER_KEYWORDS), conf)

        best  = sorted(emails, key=rank, reverse=True)[0]
        email = best.get("value", "")
        if not email:
            return None
        conf  = best.get("confidence", 0)
        return ContactResult(
            email        = email,
            email_status = "verified" if conf >= 80 else "likely",
            first_name   = best.get("first_name"),
            last_name    = best.get("last_name"),
            title        = best.get("position"),
            linkedin_url = best.get("linkedin"),
            confidence   = conf,
            source       = "hunter_domain_t1"
        )

# ── T2: Hunter email-finder ───────────────────────────────────────────────────

async def _hunter_email_finder(
    first: str, last: str, domain: str
) -> Optional[ContactResult]:
    """
    Find email for a specific person by first name + last name + domain.
    Returns None if first or last is empty, or if Hunter finds nothing.
    """
    if not first or not last:
        return None
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            "https://api.hunter.io/v2/email-finder",
            params={"domain": domain, "first_name": first,
                    "last_name": last, "api_key": HUNTER_KEY}
        )
        r.raise_for_status()
        data  = r.json().get("data") or {}
        email = data.get("email")
        if not email:
            return None
        conf  = data.get("score", 0)
        return ContactResult(
            email        = email,
            email_status = "verified" if conf >= 80 else "likely",
            first_name   = first,
            last_name    = last,
            title        = data.get("position"),
            linkedin_url = data.get("linkedin_url"),
            confidence   = conf,
            source       = "hunter_finder_t2"
        )

# ── T3: Hunter email-verifier on pattern guesses ──────────────────────────────

async def _hunter_verify_patterns(
    domain: str, title: Optional[str]
) -> Optional[ContactResult]:
    """
    Guess common email patterns based on title context.
    Verify each with Hunter. Return first that is "deliverable".
    """
    title_l  = (title or "").lower()
    if any(x in title_l for x in ["engineer", "cto", "tech", "product"]):
        patterns = [f"engineering@{domain}", f"tech@{domain}", f"hello@{domain}"]
    elif any(x in title_l for x in ["ceo", "founder", "president"]):
        patterns = [f"hello@{domain}", f"hi@{domain}", f"info@{domain}"]
    elif any(x in title_l for x in ["sales", "revenue", "gtm"]):
        patterns = [f"sales@{domain}", f"hello@{domain}", f"info@{domain}"]
    else:
        patterns = [f"hello@{domain}", f"info@{domain}", f"contact@{domain}"]

    for pattern in patterns:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.get(
                    "https://api.hunter.io/v2/email-verifier",
                    params={"email": pattern, "api_key": HUNTER_KEY}
                )
                r.raise_for_status()
                data = r.json().get("data", {})
                if data.get("result") == "deliverable":
                    return ContactResult(
                        email        = pattern,
                        email_status = "verified",
                        confidence   = data.get("score", 70),
                        source       = "hunter_verify_t3"
                    )
        except Exception:
            continue
    return None

# ── T4: Generic role email — always succeeds ──────────────────────────────────

def _generic_role_email(domain: str, title: Optional[str]) -> ContactResult:
    title_l = (title or "").lower()
    if any(x in title_l for x in ["cto", "engineer", "tech", "product"]):
        prefix = "engineering"
    elif any(x in title_l for x in ["ceo", "founder", "president"]):
        prefix = "hello"
    elif any(x in title_l for x in ["sales", "revenue", "gtm"]):
        prefix = "sales"
    else:
        prefix = "hello"
    return ContactResult(
        email        = f"{prefix}@{domain}",
        email_status = "generic",
        confidence   = 0,
        source       = "generic_t4"
    )

# ── MASTER — public interface ─────────────────────────────────────────────────

async def get_contact(
    domain: str,
    first:  str = "",
    last:   str = "",
    title:  Optional[str] = None
) -> ContactResult:
    """
    T1 Hunter domain-search → T2 Hunter email-finder →
    T3 Hunter verify patterns → T4 generic role prefix.
    Never raises. Always returns a ContactResult.
    """
    result = await try_with_circuit("hunter_domain", _hunter_domain_search, domain)
    if result:
        return result

    result = await try_with_circuit("hunter_finder", _hunter_email_finder, first, last, domain)
    if result:
        return result

    result = await try_with_circuit("hunter_verify", _hunter_verify_patterns, domain, title)
    if result:
        return result

    return _generic_role_email(domain, title)