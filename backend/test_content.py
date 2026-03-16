#!/usr/bin/env python3
"""
Test content generation directly
"""
import asyncio
import os
from content_generator_v4 import generate_content
from models import Signal, ParsedICP

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

async def test_content():
    # Mock data
    company = {"name": "Notion", "industry": "SaaS"}
    contact = {"first_name": "Sarah", "last_name": "Chen", "title": "VP Engineering", "email": "sarah.chen@notion.so"}
    
    signals = [
        Signal(
            signal_id="test1",
            type="funding",
            summary="Notion raised $275M Series C to expand AI capabilities",
            detected_at="2024-03-16",
            type_weight=1.0,
            freshness=1.0,
            icp_relevance=0.8,
            final_score=0.9
        ),
        Signal(
            signal_id="test2", 
            type="hiring",
            summary="Notion is hiring 15+ AI/ML engineers for new product initiatives",
            detected_at="2024-03-16",
            type_weight=0.9,
            freshness=1.0,
            icp_relevance=0.7,
            final_score=0.8
        )
    ]
    
    icp = ParsedICP(
        what_we_do="We provide AI automation tools for growing SaaS companies",
        target_industry="SaaS",
        target_stage="Series B",
        pain_keyword="scaling customer operations",
        solution_keyword="AI-powered workflow automation",
        buyer_titles=["CTO", "VP Engineering"],
        min_headcount=50,
        max_headcount=1000,
        threshold=35
    )
    
    content = await generate_content(company, contact, signals, icp)
    
    print("=== PROFESSIONAL EMAIL ===")
    print(f"Subject: {content.email_subject}")
    print(f"Body:\n{content.email_body}")
    print("\n=== HTML BROCHURE ===")
    print(content.brochure_html[:500] + "...")

if __name__ == "__main__":
    asyncio.run(test_content())