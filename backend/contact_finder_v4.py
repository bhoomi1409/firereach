"""
FireReach — Contact Finder v4 (Hunter only)
T1: Hunter emails already in company dict (from enrichment step)
T2: Hunter email-verifier on role patterns
T3: Generic role prefix — always succeeds
"""

import os
import httpx
from typing import Optional
from models import ContactResult

HUNTER_KEY = os.getenv("HUNTER_API_KEY", "")

_BUYER_KW = [
    "vp engineering","cto","chief technology","head of engineering",
    "head of ai","ceo","co-founder","founder","vp sales",
    "vp product","vp operations","director of engineering","chief revenue"
]

async def find_contact(company: dict, buyer_titles: list[str]) -> ContactResult:
    """
    T1: Pick best from hunter_emails in company dict.
    T2: Verify role patterns with Hunter.
    T3: Generic hello@domain fallback.
    """
    domain        = company.get("domain", "")
    hunter_emails = company.get("hunter_emails", [])
    all_buyer_kw  = _BUYER_KW + [t.lower() for t in buyer_titles]

    # T1: Hunt from already-fetched emails
    if hunter_emails:
        def rank(e: dict) -> tuple:
            pos  = (e.get("position") or "").lower()
            conf = e.get("confidence", 0)
            return (any(kw in pos for kw in all_buyer_kw), conf)

        best  = sorted(hunter_emails, key=rank, reverse=True)[0]
        email = best.get("value", "")
        if email:
            conf = best.get("confidence", 0)
            return ContactResult(
                email        = email,
                first_name   = best.get("first_name", ""),
                last_name    = best.get("last_name", ""),
                title        = best.get("position", ""),
                email_status = "verified" if conf >= 80 else "likely",
                source       = "hunter_t1",
                confidence   = conf,
            )

    # T2: Hunter verifier on role patterns
    if domain and HUNTER_KEY and len(HUNTER_KEY) > 10:
        for pattern in [f"hello@{domain}", f"info@{domain}", f"sales@{domain}"]:
            try:
                async with httpx.AsyncClient(timeout=8) as c:
                    r = await c.get(
                        "https://api.hunter.io/v2/email-verifier",
                        params={"email": pattern, "api_key": HUNTER_KEY}
                    )
                    r.raise_for_status()
                    data = r.json().get("data", {})
                    # Skip catch-all domains (every address is "deliverable")
                    if data.get("accept_all"):
                        continue
                    if data.get("result") == "deliverable":
                        return ContactResult(
                            email=pattern, email_status="verified",
                            source="hunter_verify_t2",
                            confidence=data.get("score", 70),
                        )
            except Exception:
                continue

    # T3: Generic fallback
    prefix = "hello"
    for title in buyer_titles:
        tl = title.lower()
        if any(x in tl for x in ["sales","revenue","gtm"]): prefix = "sales"; break
        if any(x in tl for x in ["engineer","tech","cto"]):  prefix = "engineering"; break

    return ContactResult(
        email=f"{prefix}@{domain}" if domain else "",
        email_status="generic",
        source="generic_t3",
    )