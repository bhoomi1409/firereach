"""
FireReach — ICP Parser
Input:  free text string from user
Output: ParsedICP with structured fields

Uses Groq to extract:
- what_we_do: what the service does
- target_industry: fintech, healthtech, saas, etc
- target_stage: series_b, series_c, startup, enterprise
- pain_keyword: the problem they have
- solution_keyword: what you solve/deliver
- buyer_titles: who buys this (list of 3-5 job titles)
- min_headcount / max_headcount: company size range
"""

import os
import json
import httpx
from pathlib import Path
from models import ParsedICP

# Load environment variables
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

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
SERPER_KEY = os.getenv("SERP_API_KEY", "")

print(f"DEBUG: ICP Parser - GROQ_KEY length: {len(GROQ_KEY)}")
print(f"DEBUG: ICP Parser - SERPER_KEY length: {len(SERPER_KEY)}")

PARSE_SYSTEM = """You extract structured ICP (Ideal Customer Profile) data from free-text service descriptions.
Return ONLY valid JSON, no markdown, no explanation.

JSON schema:
{
  "what_we_do": "one sentence describing the service",
  "target_industry": "primary industry keyword (saas/fintech/healthtech/edtech/ai/ecommerce/b2b)",
  "target_stage": "funding stage (series_a/series_b/series_c/startup/enterprise/scaleup)",
  "pain_keyword": "the core problem they have that you solve (5-10 words)",
  "solution_keyword": "what you deliver / the outcome (5-10 words)",
  "buyer_titles": ["3-5 job titles who would buy this"],
  "min_headcount": 50,
  "max_headcount": 5000
}

Rules:
- target_industry: pick the SINGLE most relevant keyword
- buyer_titles: be specific — not just "manager" but "VP of Customer Success"
- pain_keyword: extract the PROBLEM, not the solution
- If stage not mentioned: default to "series_b"
- If size not mentioned: default to 50-5000"""
async def parse_icp(icp_text: str) -> ParsedICP:
    """
    Parse free-text ICP description into structured ParsedICP.
    Returns defaults if parsing fails.
    """
    if len(icp_text.strip()) < 20:
        raise ValueError("ICP text too short — please describe your service in at least 20 characters")

    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": PARSE_SYSTEM},
                        {"role": "user", "content": f"Extract ICP from this text:\n\n{icp_text}"}
                    ],
                    "max_tokens": 400,
                    "temperature": 0.1   # low temp for structured extraction
                }
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"]

        # Strip any markdown fences if LLM added them
        raw = raw.strip()
        FENCE = chr(96)*3
        if raw.startswith(FENCE):
            raw = raw.split(FENCE)[1]
            if raw.startswith("json"): raw = raw[4:]
        data = json.loads(raw)
        return ParsedICP(
            what_we_do       = data.get("what_we_do", icp_text[:100]),
            target_industry  = data.get("target_industry", "saas"),
            target_stage     = data.get("target_stage", "series_b"),
            pain_keyword     = data.get("pain_keyword", ""),
            solution_keyword = data.get("solution_keyword", ""),
            buyer_titles     = data.get("buyer_titles", ["CTO", "VP Engineering", "CEO"]),
            min_headcount    = int(data.get("min_headcount", 50)),
            max_headcount    = int(data.get("max_headcount", 5000)),
        )

    except Exception as e:
        return ParsedICP(
            what_we_do       = icp_text[:200],
            target_industry  = "saas",
            target_stage     = "series_b",
            pain_keyword     = icp_text[:80],
            solution_keyword = icp_text[:80],
            buyer_titles     = ["CTO", "VP Engineering", "CEO", "Co-Founder"],
        )