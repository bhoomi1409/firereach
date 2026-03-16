"""
FireReach — ICP Scorer v4
3 dimensions: company_fit (40pts) + pain_match (40pts) + structural (20pts)
Gate: total < threshold → skip
"""

import re, math
from models import ParsedICP

_SYNS = {
    "saas":       ["software","cloud","b2b","subscription","platform"],
    "fintech":    ["payments","banking","financial","lending"],
    "startup":    ["early stage","seed","series a","growing"],
    "hiring":     ["recruiting","job posting","open roles"],
    "funding":    ["raised","investment","series","venture","backed"],
}

def _expand(text: str) -> str:
    t = text.lower()
    extra = []
    for k, v in _SYNS.items():
        if k in t: extra.extend(v)
    return t + " " + " ".join(extra)

def _vec(text: str) -> dict:
    toks = re.findall(r'\b[a-z0-9]+\b', _expand(text))
    if not toks: return {}
    freq: dict = {}
    for t in toks: freq[t] = freq.get(t, 0) + 1
    n = len(toks)
    return {t: c/n for t, c in freq.items()}

def _sim(a: str, b: str) -> float:
    va = _vec(a); vb = _vec(b)
    keys = set(va) | set(vb)
    dot  = sum(va.get(k,0)*vb.get(k,0) for k in keys)
    ma   = math.sqrt(sum(v*v for v in va.values()))
    mb   = math.sqrt(sum(v*v for v in vb.values()))
    return dot/(ma*mb) if ma and mb else 0.0

def score_company(company: dict, icp: ParsedICP) -> tuple[float, str, bool]:
    """
    Returns (score, reason_str, should_proceed).
    should_proceed = score >= icp.threshold
    """
    corpus = " ".join([
        company.get("description", ""),
        company.get("industry", ""),
        " ".join(company.get("keywords", [])),
        " ".join(company.get("web_snippets", [])[:2]),
    ]).strip()

    # If no corpus data, use company name and domain for basic matching
    if not corpus:
        corpus = f"{company.get('name', '')} {company.get('domain', '')} {company.get('reason', '')}"

    # Dimension 1: company fit (what_they_do match)
    fit_text = f"{icp.target_industry} {icp.target_stage}"
    fit = _sim(fit_text, corpus)
    
    # Boost fit score for industry matches in company name/domain/reason
    corpus_lower = corpus.lower()
    if icp.target_industry.lower() in corpus_lower:
        fit = max(fit, 0.3)  # Minimum 30% if industry mentioned
    if any(word in corpus_lower for word in ["fintech", "financial", "banking", "payments"]) and icp.target_industry == "fintech":
        fit = max(fit, 0.4)  # 40% for fintech keywords
    if any(word in corpus_lower for word in ["saas", "software", "platform", "cloud"]) and icp.target_industry == "saas":
        fit = max(fit, 0.4)  # 40% for SaaS keywords
        
    fit_pts = round(fit * 40, 1)

    # Dimension 2: pain match (why_they_need_us)
    pain = _sim(icp.pain_keyword, corpus)
    
    # Boost pain score for common business challenges
    pain_keywords = ["scaling", "automation", "efficiency", "support", "operations", "growth"]
    if any(word in corpus_lower for word in pain_keywords):
        pain = max(pain, 0.2)  # Minimum 20% for business challenges
        
    pain_pts = round(pain * 40, 1)

    # Dimension 3: structural
    struct = 0
    hc = company.get("headcount") or 0
    if icp.min_headcount <= hc <= icp.max_headcount: 
        struct += 12
    elif hc > 0: 
        struct += 4
    else:
        # Default points for demo companies without headcount data
        struct += 8
        
    fs = (company.get("funding", "")).lower().replace(" ", "_")
    good = ["series_a", "series_b", "series_c"]
    if fs in good: 
        struct += 8
    elif fs in ["seed", "series_d"]: 
        struct += 4
    elif "series" in corpus_lower or "funded" in corpus_lower:
        # Default points for companies mentioning funding
        struct += 6

    # Negative signal hard block
    neg_kw = ["layoffs", "bankrupt", "shutting down", "restructuring", "acquired"]
    desc = " ".join([company.get("description","")]
                    + [n.get("title","") for n in company.get("news",[])[:3]]).lower()
    for kw in neg_kw:
        if kw in desc:
            return 0.0, f"negative signal: '{kw}'", False

    total = round(min(100, fit_pts + pain_pts + struct), 1)
    reason = f"fit={fit:.0%} pain={pain:.0%} struct={struct}/20"
    return total, reason, total >= icp.threshold