"""
FireReach — Company Discovery v4 (uses ParsedICP for smarter queries)
Input:  ParsedICP
Output: list[DiscoveredCompany]
"""

import os
import re
import asyncio
import httpx
from urllib.parse import urlparse
from models import ParsedICP, DiscoveredCompany

# Load environment variables
import os
from pathlib import Path

# Try multiple paths for .env file
env_paths = [
    '.env',  # Current directory
    Path(__file__).parent / '.env',  # Same directory as this file
    Path(__file__).parent.parent / '.env',  # Parent directory
]

for env_path in env_paths:
    if Path(env_path).exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            break
        except ImportError:
            # Fallback: load .env manually
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
                break
            except Exception:
                continue

SERPER_KEY = os.getenv("SERP_API_KEY", "")

print(f"DEBUG: Company Discovery - SERPER_KEY length: {len(SERPER_KEY)}")

_BLACKLIST = {
    "google", "apple", "microsoft", "amazon", "meta", "netflix",
    "salesforce", "oracle", "sap", "ibm", "cisco", "intel",
    "techcrunch", "forbes", "reuters", "bloomberg", "venturebeat",
    "crunchbase", "linkedin", "twitter", "facebook", "instagram",
    "indeed", "glassdoor", "ziprecruiter", "monster", "naukri",
    # VC firms and investors
    "andreessen", "horowitz", "sequoia", "benchmark", "kleiner", "perkins",
    "accel", "greylock", "founders", "fund", "capital", "ventures",
    "partners", "equity", "investment", "investments", "investor", "investors",
    # Common words that appear in financial contexts
    "here", "there", "they", "them", "this", "that", "these", "those",
    "what", "when", "where", "which", "while", "with", "without",
    "according", "including", "following", "during", "between", "through",
}

def _build_queries(icp: ParsedICP) -> list[tuple[str, str]]:
    """
    Returns list of (query_string, reason_tag) tuples.
    reason_tag = why companies from this query are relevant.
    """
    stage    = icp.target_stage.replace("_", " ")
    industry = icp.target_industry
    
    return [
        (
            f'"{industry}" companies "series b" OR "series c" funding 2024 2025 site:techcrunch.com',
            "recent funding"
        ),
        (
            f'fastest growing {industry} startups 2024 2025 list',
            "growth companies"
        ),
        (
            f'{industry} companies hiring "CTO" OR "VP Engineering" 2024 2025',
            "hiring executives"
        ),
        (
            f'top {industry} companies {stage} funding raised',
            "funded companies"
        ),
        (
            f'{industry} startups unicorn valuation 2024 2025',
            "high-value companies"
        ),
    ]

def _extract_names(results: list[dict], reason: str) -> list[DiscoveredCompany]:
    """Extract company names from Serper organic results using conservative patterns."""
    companies = []
    
    # Most reliable pattern: "CompanyName, a description, raised $X"
    company_desc_re = re.compile(
        r'\b([A-Z][a-zA-Z0-9]+(?:\s[A-Z][a-zA-Z0-9]+)?),\s+a\s+[^,]+,\s+raised',
        re.IGNORECASE
    )

    for item in results:
        title   = item.get("title", "")
        snippet = item.get("snippet", "")
        link    = item.get("link", "")

        # Primary extraction: "CompanyName, a fintech startup, raised"
        for text in [title, snippet]:
            for match in company_desc_re.finditer(text):
                name = match.group(1).strip()
                if _valid_name(name):
                    domain = _domain_from_link(link)
                    companies.append(DiscoveredCompany(name=name, domain=domain, reason=reason, is_demo=False))

        # From quoted names in snippet (company names often in quotes)
        for q in re.findall(r'"([A-Z][a-zA-Z0-9\s]{4,25})"', snippet):
            name = q.strip()
            if _valid_name(name) and len(name.split()) <= 3:  # Max 3 words
                companies.append(DiscoveredCompany(name=name, domain="", reason=reason, is_demo=False))

        # From domain slug (very selective - only for known startup domains)
        netloc = urlparse(link).netloc.replace("www.", "")
        if netloc and netloc.endswith(('.io', '.ai', '.co', '.app')) and not any(x in netloc for x in ["techcrunch.com", "crunchbase.com", "linkedin.com", "bloomberg.com", "reuters.com", "forbes.com"]):
            domain_name = netloc.split(".")[0] if netloc else ""
            if len(domain_name) > 3 and domain_name.lower() not in _BLACKLIST and _valid_name(domain_name.capitalize()):
                companies.append(DiscoveredCompany(
                    name=domain_name.capitalize(), domain=netloc, reason=reason, is_demo=False))

    return companies

def _valid_name(name: str) -> bool:
    nl = name.lower().strip()
    if len(name) < 3 or len(name) > 40: return False
    if nl in _BLACKLIST: return False
    if name.isdigit(): return False
    
    # Allow mixed case names (not just all lowercase)
    if not re.match(r'^[A-Za-z][A-Za-z0-9\s]*$', name): return False
    
    # Common non-company words to filter out
    bad_words = {
        "how to", "best of", "top 10", "what is", "here they", "the top", "list of",
        "series", "nvidia", "founded", "latino", "felix", "funding", "raised",
        "startup", "company", "companies", "fintech", "platform", "service",
        "million", "billion", "round", "investment", "capital", "ventures",
        "it has", "investors", "according", "including", "following", "during",
        "between", "through", "within", "without", "against", "before", "after",
        "above", "below", "under", "over", "into", "onto", "upon", "with",
        "from", "about", "around", "across", "along", "among", "behind",
        "beside", "beyond", "inside", "outside", "toward", "towards", "until",
        "while", "since", "because", "although", "though", "unless", "whereas",
        "whether", "however", "therefore", "moreover", "furthermore", "nevertheless",
        "meanwhile", "otherwise", "instead", "besides", "indeed", "certainly",
        "obviously", "apparently", "perhaps", "probably", "possibly", "likely",
        "unlikely", "definitely", "absolutely", "completely", "entirely", "totally"
    }
    if nl in bad_words: return False
    
    # Must have at least one uppercase letter (proper noun)
    if not any(c.isupper() for c in name): return False
    
    # Filter out common words that appear in financial contexts
    if nl in ["series", "round", "funding", "raised", "million", "billion"]: return False
    
    # Must not be a common English word
    common_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let", "put", "say", "she", "too", "use"}
    if nl in common_words: return False
    
    return True

def _domain_from_link(link: str) -> str:
    try:
        return urlparse(link).netloc.replace("www.", "")
    except Exception:
        return ""

def _deduplicate(companies: list[DiscoveredCompany]) -> list[DiscoveredCompany]:
    seen   = set()
    result = []
    for c in companies:
        key = c.name.lower().strip()
        if key in seen or key in _BLACKLIST:
            continue
        seen.add(key)
        result.append(c)
    return result

async def discover_companies(icp: ParsedICP, target_count: int = 15) -> list[DiscoveredCompany]:
    print(f"DEBUG: discover_companies called with industry={icp.target_industry}, target_count={target_count}")
    print(f"DEBUG: SERPER_KEY length: {len(SERPER_KEY)}")
    
    # For now, use high-quality demo companies that are realistic and relevant
    # The Serper extraction needs more work to be reliable
    print("DEBUG: Using high-quality demo companies (Serper extraction needs refinement)")
    return _get_demo_companies(icp, target_count)

def _get_demo_companies(icp: ParsedICP, target_count: int) -> list[DiscoveredCompany]:
    """Return realistic demo companies based on ICP for testing when API is unavailable"""
    
    # High-quality fintech companies by category
    fintech_companies = [
        ("Stripe", "stripe.com", "payments platform - Series H funded"),
        ("Plaid", "plaid.com", "financial data API - Series D funded"),
        ("Chime", "chime.com", "digital banking - Series F funded"),
        ("Robinhood", "robinhood.com", "investment platform - Series G funded"),
        ("Coinbase", "coinbase.com", "crypto exchange - Public"),
        ("Square", "squareup.com", "payments platform - Public"),
        ("Affirm", "affirm.com", "buy now pay later - Public"),
        ("SoFi", "sofi.com", "personal finance - Public"),
        ("Klarna", "klarna.com", "buy now pay later - Series H funded"),
        ("Revolut", "revolut.com", "digital banking - Series E funded"),
        ("Nubank", "nubank.com.br", "digital banking - Series G funded"),
        ("Monzo", "monzo.com", "digital banking - Series F funded"),
        ("N26", "n26.com", "digital banking - Series D funded"),
        ("Wise", "wise.com", "money transfer - Public"),
        ("Rapyd", "rapyd.net", "fintech infrastructure - Series E funded"),
    ]
    
    # High-quality SaaS companies
    saas_companies = [
        ("Notion", "notion.so", "productivity workspace - Series C funded"),
        ("Linear", "linear.app", "issue tracking - Series B funded"),
        ("Retool", "retool.com", "internal tools - Series B funded"),
        ("Webflow", "webflow.com", "web design platform - Series A funded"),
        ("Vercel", "vercel.com", "frontend platform - Series B funded"),
        ("Supabase", "supabase.com", "database platform - Series A funded"),
        ("Clerk", "clerk.dev", "authentication - Series A funded"),
        ("Resend", "resend.com", "email API - Series A funded"),
        ("PlanetScale", "planetscale.com", "database platform - Series B funded"),
        ("Railway", "railway.app", "deployment platform - Series A funded"),
        ("Neon", "neon.tech", "serverless postgres - Series A funded"),
        ("Upstash", "upstash.com", "serverless data - Series A funded"),
        ("Convex", "convex.dev", "backend platform - Series A funded"),
        ("Temporal", "temporal.io", "workflow platform - Series B funded"),
        ("Hasura", "hasura.io", "GraphQL platform - Series B funded"),
    ]
    
    # High-quality AI companies
    ai_companies = [
        ("OpenAI", "openai.com", "AI research - Series C funded"),
        ("Anthropic", "anthropic.com", "AI safety - Series C funded"),
        ("Perplexity", "perplexity.ai", "AI search - Series B funded"),
        ("Runway", "runwayml.com", "AI video - Series C funded"),
        ("Jasper", "jasper.ai", "AI writing - Series A funded"),
        ("Copy.ai", "copy.ai", "AI copywriting - Series A funded"),
        ("Synthesia", "synthesia.io", "AI video - Series B funded"),
        ("Midjourney", "midjourney.com", "AI art - Series A funded"),
        ("Stability AI", "stability.ai", "AI models - Series A funded"),
        ("Cohere", "cohere.ai", "AI platform - Series B funded"),
        ("Hugging Face", "huggingface.co", "AI platform - Series B funded"),
        ("Scale AI", "scale.com", "AI data platform - Series E funded"),
        ("Weights & Biases", "wandb.ai", "ML platform - Series C funded"),
        ("Replicate", "replicate.com", "ML platform - Series A funded"),
        ("Together AI", "together.ai", "AI platform - Series A funded"),
    ]
    
    # Select based on ICP industry
    if icp.target_industry in ["fintech", "financial", "payments", "banking"]:
        selected = fintech_companies
    elif icp.target_industry in ["ai", "artificial intelligence", "machine learning", "ml"]:
        selected = ai_companies
    else:
        selected = saas_companies
    
    companies = []
    for name, domain, reason in selected[:target_count]:
        companies.append(DiscoveredCompany(
            name=name,
            domain=domain, 
            reason=reason,
            is_demo=True  # Mark as demo company
        ))
    
    return companies