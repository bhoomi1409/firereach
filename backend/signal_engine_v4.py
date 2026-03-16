"""
FireReach — 7-Signal Engine v4
S1 Hiring       weight=0.85  detect AI/ML/buyer-role job postings
S2 Funding      weight=1.00  detect funding rounds from news/snippets
S3 Product      weight=0.75  detect product launches / new features
S4 Tech gap     weight=0.70  detect absence of relevant tech in stack
S5 Exec hire    weight=0.95  detect new VP/CTO/CEO just joined
S6 Competitor   weight=0.80  detect competitor acquired or shut down
S7 News mention weight=0.55  any recent press mention (lowest weight)
"""

import re
import math
import hashlib
from datetime import datetime
from models import Signal, ParsedICP

# ── SIGNAL TYPE WEIGHTS ──────────────────────────────────────────────────────
SIGNAL_WEIGHTS = {
    "funding":      1.00,
    "exec_hire":    0.95,
    "hiring":       0.85,
    "competitor":   0.80,
    "product":      0.75,
    "tech_gap":     0.70,
    "news":         0.55,
}

# ── DETECTION KEYWORDS PER SIGNAL TYPE ──────────────────────────────────────
_FUNDING_KW    = ["raised", "series a", "series b", "series c", "seed round",
                  "funding", "investment", "valuation", "backed by", "led by"]
_EXEC_KW       = ["appointed", "joins as", "named as", "hired as",
                  "vp of", "chief ", "head of", "director of", "new cto", "new ceo"]
_HIRING_KW     = ["engineer", "developer", "ml engineer", "ai engineer",
                  "data scientist", "technical lead", "software", "hiring"]
_COMPETITOR_KW = ["acquired by", "acquisition", "shut down", "shutdown",
                  "bankrupt", "merger", "merges with"]
_PRODUCT_KW    = ["launches", "launched", "announces", "new feature",
                  "new product", "releases", "ships", "introduces"]

# ── SEMANTIC ENGINE ──────────────────────────────────────────────────────────
_SYNS = {
    "saas":       ["software", "cloud", "b2b", "subscription"],
    "fintech":    ["payments", "banking", "financial", "lending"],
    "hiring":     ["recruiting", "job", "open roles", "headcount"],
    "funding":    ["raised", "investment", "series", "venture"],
    "automation": ["automate", "ai", "workflow", "efficiency"],
}

def _expand(text: str) -> str:
    t = text.lower()
    extra = []
    for k, v in _SYNS.items():
        if k in t:
            extra.extend(v)
    return t + " " + " ".join(extra)

def _vec(text: str) -> dict:
    toks = re.findall(r'\b[a-z0-9]+\b', _expand(text))
    if not toks: return {}
    freq: dict = {}
    for t in toks: freq[t] = freq.get(t, 0) + 1
    n = len(toks)
    return {t: c/n for t, c in freq.items()}

def _cosine(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    dot  = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    ma   = math.sqrt(sum(v*v for v in a.values()))
    mb   = math.sqrt(sum(v*v for v in b.values()))
    return dot / (ma * mb) if ma and mb else 0.0

def _sim(a: str, b: str) -> float:
    return round(_cosine(_vec(a), _vec(b)), 3)

def _freshness(date_str: str) -> float:
    """1.0 = today, 0.0 = 90+ days ago."""
    if not date_str: return 0.5
    try:
        dt   = datetime.fromisoformat(date_str.replace("Z", "").split("+")[0])
        days = (datetime.utcnow() - dt).days
        return max(0.0, 1.0 - days / 90)
    except Exception:
        return 0.5

def _detect_type(text: str) -> str:
    tl = text.lower()
    if any(k in tl for k in _FUNDING_KW):    return "funding"
    if any(k in tl for k in _EXEC_KW):       return "exec_hire"
    if any(k in tl for k in _COMPETITOR_KW): return "competitor"
    if any(k in tl for k in _PRODUCT_KW):    return "product"
    if any(k in tl for k in _HIRING_KW):     return "hiring"
    return "news"

def _make_id(summary: str) -> str:
    return hashlib.sha256(summary.encode()).hexdigest()[:12]

def extract_signals(company: dict, icp: ParsedICP) -> list[Signal]:
    """
    Extract all signals from enriched company data.
    Score each. Rerank. Return top 5 (top 3 go into email).
    """
    icp_text   = f"{icp.what_we_do} {icp.pain_keyword} {icp.solution_keyword}"
    raw_signals = []  # list of (summary, detected_at)

    # From news articles
    for article in company.get("news", []):
        summary = article.get("title", "") or article.get("description", "")
        if summary and len(summary) > 20:
            raw_signals.append((summary, article.get("published_at", "")))

    # From job snippets
    for snippet in company.get("job_snippets", []):
        raw_signals.append((f"Hiring: {snippet[:100]}", datetime.utcnow().isoformat()))

    # From web snippets
    for snippet in company.get("web_snippets", []):
        raw_signals.append((snippet[:120], datetime.utcnow().isoformat()))

    # Tech gap signal (S4) — if no modern AI tech detected
    tech = [t.lower() for t in company.get("technologies", [])]
    ai_tech = ["langchain", "openai", "anthropic", "huggingface", "pytorch", "tensorflow"]
    if not any(at in tech for at in ai_tech):
        raw_signals.append((
            f"No advanced AI tooling detected in tech stack — gap for {icp.solution_keyword}",
            datetime.utcnow().isoformat()
        ))

    # Score every signal
    scored = []
    seen_ids = set()
    for summary, detected_at in raw_signals:
        sid = _make_id(summary)
        if sid in seen_ids:
            continue
        seen_ids.add(sid)

        sig_type  = _detect_type(summary)
        tw        = SIGNAL_WEIGHTS.get(sig_type, 0.5)
        fr        = _freshness(detected_at)
        rel       = _sim(summary, icp_text)
        final     = round(tw * 0.30 + fr * 0.35 + rel * 0.35, 3)

        scored.append(Signal(
            signal_id     = sid,
            type          = sig_type,
            summary       = summary,
            detected_at   = detected_at or datetime.utcnow().isoformat(),
            type_weight   = tw,
            freshness     = fr,
            icp_relevance = rel,
            final_score   = final,
        ))

    # Sort by final_score descending, return top 5
    scored.sort(key=lambda s: s.final_score, reverse=True)
    return scored[:5]