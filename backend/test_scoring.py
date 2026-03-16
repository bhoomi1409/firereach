#!/usr/bin/env python3
"""
Test ICP scoring directly
"""
from icp_scorer_v4 import score_company
from models import ParsedICP

# Test ICP
icp = ParsedICP(
    what_we_do="We build AI voice agents for fintech companies",
    target_industry="fintech",
    target_stage="series_b",
    pain_keyword="customer support automation",
    solution_keyword="AI voice agents",
    buyer_titles=["CTO", "VP Engineering"],
    min_headcount=50,
    max_headcount=1000,
    threshold=15
)

# Test companies
companies = [
    {"name": "Ramp", "domain": "ramp.com", "reason": "real company: expense management - Series C funded"},
    {"name": "Mercury", "domain": "mercury.com", "reason": "real company: business banking - Series B funded"},
    {"name": "Brex", "domain": "brex.com", "reason": "real company: corporate cards - Series C funded"},
]

print("🧪 Testing ICP Scoring")
print("=" * 50)
print(f"ICP: {icp.what_we_do}")
print(f"Industry: {icp.target_industry}")
print(f"Threshold: {icp.threshold}")
print()

for company in companies:
    score, reason, should_proceed = score_company(company, icp)
    print(f"Company: {company['name']}")
    print(f"  Score: {score}% ({reason})")
    print(f"  Pass: {'✅' if should_proceed else '❌'}")
    print(f"  Reason: {company['reason']}")
    print()