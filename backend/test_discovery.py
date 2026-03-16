#!/usr/bin/env python3
"""
Test company discovery directly
"""
import asyncio
import os
from company_discovery_v4 import discover_companies
from models import ParsedICP

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

async def test_discovery():
    print("🧪 Testing Company Discovery")
    print("=" * 40)
    
    # Test ICP
    icp = ParsedICP(
        what_we_do="We provide AI-powered customer success automation for Series B SaaS companies",
        target_industry="saas",
        target_stage="series_b",
        pain_keyword="scaling support operations",
        solution_keyword="AI automation",
        buyer_titles=["CTO", "VP Engineering"],
        min_headcount=50,
        max_headcount=1000,
        threshold=25
    )
    
    print(f"ICP Industry: {icp.target_industry}")
    print(f"ICP Stage: {icp.target_stage}")
    
    companies = await discover_companies(icp, target_count=5)
    
    print(f"\n✅ Companies discovered: {len(companies)}")
    for i, company in enumerate(companies, 1):
        print(f"{i}. {company.name} ({company.domain}) - {company.reason}")

if __name__ == "__main__":
    asyncio.run(test_discovery())