"""
FireReach — Company Discovery
Input:  ICP (3 plain English strings)
Output: list of company names to target

Strategy:
  1. Build 4-6 smart search queries from ICP fields
  2. Search Serper for each query
  3. Extract company names from search results
  4. Deduplicate + clean
  5. Return list of candidate company names
"""

import os
import re
import asyncio
import httpx
from typing import Optional

SERPER_KEY = os.getenv("SERPER_API_KEY", "")

# ── QUERY BUILDER ─────────────────────────────────────────────────────────────

def build_discovery_queries(
    what_we_do: str,
    what_they_do: str,
    why_they_need_us: str
) -> list[str]:
    """
    Build multiple targeted search queries from ICP fields.
    More queries = more candidate companies = better coverage.

    Strategy:
    - Query 1: Target company type + funding signal
    - Query 2: Target company type + hiring signal
    - Query 3: Pain point companies + recent news
    - Query 4: Industry + company size
    - Query 5: Problem keyword companies
    - Query 6: Competitor customers (if detectable)

    Examples for ICP "Series B SaaS with sales team, low reply rates":
    - "Series B SaaS company raised funding 2024 2025"
    - "SaaS startup hiring VP Sales OR SDR 2025"
    - "B2B SaaS companies low reply rates outreach"
    - "SaaS Series B companies 50 500 employees"
    - "sales automation tools B2B SaaS"
    """
    queries = []

    # Extract key phrases from ICP fields
    target = what_they_do.lower()
    pain   = why_they_need_us.lower()

    # Q1: Company type + funding (high intent)
    queries.append(f'"{what_they_do[:60]}" raised funding 2024 OR 2025 site:techcrunch.com OR site:crunchbase.com')

    # Q2: Company type + hiring (growth signal)
    queries.append(f'{what_they_do[:50]} hiring "VP Sales" OR "Head of Sales" OR "SDR" 2025')

    # Q3: Pain point search
    queries.append(f'companies "{why_they_need_us[:50]}" B2B SaaS')

    # Q4: Industry size
    if "series b" in target or "series c" in target:
        queries.append(f'list of "Series B" OR "Series C" SaaS companies 2024 2025')
    elif "startup" in target:
        queries.append(f'fast-growing B2B SaaS startups 2024 2025 funding')
    else:
        queries.append(f'{what_they_do[:40]} companies list 2025')

    # Q5: Product/pain keyword search
    queries.append(f'B2B SaaS companies {why_they_need_us[:40]} problem solution')

    return queries[:5]   # cap at 5 queries to stay within Serper free tier

# ── COMPANY NAME EXTRACTOR ────────────────────────────────────────────────────

# Known non-company words to filter out from extracted names
_BLACKLIST = {
    "techcrunch", "crunchbase", "linkedin", "twitter", "facebook",
    "google", "apple", "microsoft", "amazon", "meta", "netflix",
    "the company", "this company", "our company", "their company",
    "inc", "llc", "ltd", "corp", "company", "startup", "saas",
    "b2b", "series", "funding", "venture", "capital", "investors",
    "top", "best", "list", "guide", "how", "what", "why", "when",
    "new", "latest", "recent", "update", "news", "blog", "post",
}

def extract_company_names(search_results: list[dict]) -> list[str]:
    """
    Extract company names from Serper organic search results.

    Sources:
    - result["title"]: often contains company name
    - result["snippet"]: company mentioned in context
    - result["link"]: domain name can be company name

    Heuristics:
    - Title Case words that are NOT common English words
    - Words before "raises", "hired", "launches", "announces"
    - Domain name (strip .com/.io/.co)
    - Company names in quotes in snippets
    """
    companies = []

    for result in search_results:
        title   = result.get("title", "")
        snippet = result.get("snippet", "")
        link    = result.get("link", "")

        # Extract from title: "CompanyName Raises $50M Series B"
        # Pattern: Title Case word(s) before action verbs
        action_pattern = re.compile(
            r'^([A-Z][a-zA-Z0-9]+(?:\s[A-Z][a-zA-Z0-9]+)?)\s+'
            r'(?:raises|raised|launches|launched|hires|hired|announces|expands|closes)',
            re.MULTILINE
        )
        for match in action_pattern.finditer(title):
            name = match.group(1).strip()
            if _is_valid_company_name(name):
                companies.append(name)

        # Extract company names in quotes from snippets
        quoted = re.findall(r'"([A-Z][a-zA-Z0-9\s]{2,30})"', snippet)
        for q in quoted:
            if _is_valid_company_name(q.strip()):
                companies.append(q.strip())

        # Extract from domain (deel.com → Deel, hubspot.com → HubSpot)
        domain_match = re.search(r'https?://(?:www\.)?([a-z0-9-]+)\.',  link)
        if domain_match:
            domain_name = domain_match.group(1)
            # Convert slug to title: hubspot → HubSpot (capitalize)
            if len(domain_name) > 2 and domain_name not in _BLACKLIST:
                companies.append(domain_name.capitalize())

    return companies

def _is_valid_company_name(name: str) -> bool:
    """Validate extracted company name candidate."""
    name_l = name.lower().strip()

    # Too short or too long
    if len(name) < 3 or len(name) > 40:
        return False

    # Is in blacklist
    if name_l in _BLACKLIST:
        return False

    # Contains only lowercase (probably not a company name)
    if name == name.lower():
        return False

    # Is a number
    if name.isdigit():
        return False

    # Contains obviously non-company words
    bad_words = ["how to", "what is", "best of", "top 10", "guide to"]
    if any(bw in name_l for bw in bad_words):
        return False

    return True

# ── DEDUPLICATION ─────────────────────────────────────────────────────────────

def deduplicate_companies(names: list[str]) -> list[str]:
    """
    Remove duplicates. Normalize names.
    Also remove companies that are obviously too large (FAANG etc.)
    or obviously wrong (news sites, etc.)
    """
    ALWAYS_EXCLUDE = {
        "google", "apple", "microsoft", "amazon", "meta", "netflix",
        "salesforce", "oracle", "sap", "ibm", "cisco", "intel",
        "techcrunch", "forbes", "reuters", "bloomberg", "venturebeat",
        "crunchbase", "linkedin", "twitter", "facebook", "instagram",
    }

    seen   = set()
    result = []

    for name in names:
        normalized = name.strip().lower()
        if normalized in seen:
            continue
        if normalized in ALWAYS_EXCLUDE:
            continue
        seen.add(normalized)
        result.append(name.strip())

    return result

# ── MASTER DISCOVERY FUNCTION ─────────────────────────────────────────────────

async def discover_companies(
    what_we_do:       str,
    what_they_do:     str,
    why_they_need_us: str,
    target_count:     int = 15,   # how many candidates to return
) -> list[str]:
    """
    Main entry point. Given ICP, return list of company name candidates.

    Process:
    1. Build smart queries from ICP
    2. Run all queries against Serper
    3. Extract company names from all results
    4. Deduplicate and clean
    5. Return top `target_count` candidates

    The caller (orchestrator) will then enrich + score each one,
    so we return more than needed to account for ICP filtering.
    """
    queries        = build_discovery_queries(what_we_do, what_they_do, why_they_need_us)
    all_results    = []
    all_companies  = []

    # Run all queries (with concurrency limit to avoid Serper rate limit)
    semaphore = asyncio.Semaphore(2)   # max 2 concurrent Serper calls

    async def run_query(query: str) -> list[dict]:
        async with semaphore:
            try:
                async with httpx.AsyncClient(timeout=8) as c:
                    r = await c.post(
                        "https://google.serper.dev/search",
                        headers={
                            "X-API-KEY":    SERPER_KEY,
                            "Content-Type": "application/json"
                        },
                        json={"q": query, "num": 10}
                    )
                    r.raise_for_status()
                    return r.json().get("organic", [])
            except Exception:
                return []

    tasks   = [run_query(q) for q in queries]
    results = await asyncio.gather(*tasks)

    for result_list in results:
        all_results.extend(result_list)

    # Extract company names from all results
    all_companies = extract_company_names(all_results)

    # Deduplicate
    unique = deduplicate_companies(all_companies)

    # Return up to target_count candidates
    # Shuffle slightly to avoid always picking same companies
    return unique[:target_count]