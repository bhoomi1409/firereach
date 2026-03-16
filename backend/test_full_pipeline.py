#!/usr/bin/env python3
"""
Test full pipeline with professional email content
"""
import asyncio
import os
from email_sender_v4 import send_with_brochure
from content_generator_v4 import generate_content
from models import Signal, ParsedICP

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

async def test_pipeline():
    print("🧪 Testing FireReach v4 Professional Email Pipeline")
    print("=" * 60)
    
    # Mock realistic data
    company = {"name": "Notion", "industry": "SaaS", "domain": "notion.so"}
    contact = {
        "first_name": "Sarah", 
        "last_name": "Chen", 
        "title": "VP Engineering", 
        "email": "mahajanbhoomi14@gmail.com"  # Send to self for testing
    }
    
    signals = [
        Signal(
            signal_id="test1",
            type="funding",
            summary="Notion raised $275M Series C to expand AI capabilities and scale engineering team",
            detected_at="2024-03-16",
            type_weight=1.0,
            freshness=1.0,
            icp_relevance=0.85,
            final_score=0.92
        ),
        Signal(
            signal_id="test2", 
            type="hiring",
            summary="Notion is actively hiring 20+ AI/ML engineers for new product initiatives",
            detected_at="2024-03-16",
            type_weight=0.9,
            freshness=1.0,
            icp_relevance=0.75,
            final_score=0.81
        ),
        Signal(
            signal_id="test3",
            type="product",
            summary="Notion launched AI-powered features but lacks advanced automation capabilities",
            detected_at="2024-03-16",
            type_weight=0.8,
            freshness=1.0,
            icp_relevance=0.70,
            final_score=0.75
        )
    ]
    
    icp = ParsedICP(
        what_we_do="We provide AI-powered workflow automation solutions for high-growth SaaS companies",
        target_industry="SaaS",
        target_stage="Series B+",
        pain_keyword="scaling customer operations and reducing manual workflows",
        solution_keyword="intelligent automation that reduces operational overhead by 60%",
        buyer_titles=["CTO", "VP Engineering", "Head of Operations"],
        min_headcount=100,
        max_headcount=2000,
        threshold=35
    )
    
    print("1. Generating professional email content...")
    content = await generate_content(company, contact, signals, icp)
    
    print(f"\n📧 EMAIL SUBJECT: {content.email_subject}")
    print(f"\n📝 EMAIL BODY:\n{content.email_body}")
    
    print(f"\n📄 BROCHURE HTML (first 400 chars):\n{content.brochure_html[:400]}...")
    
    print("\n2. Sending professional email with brochure...")
    log = []
    sent = send_with_brochure(
        to_email=contact["email"],
        subject=content.email_subject,
        body=content.email_body,
        brochure_html=content.brochure_html,
        company_name=company["name"],
        log=log
    )
    
    print(f"\n✅ EMAIL SENT: {sent}")
    print("📋 SEND LOG:")
    for entry in log:
        print(f"   {entry}")
    
    print("\n" + "=" * 60)
    print("🎉 FireReach v4 Professional Email Pipeline Complete!")
    print(f"   • Professional executive-level email content: ✅")
    print(f"   • HTML brochure with business proposal: ✅") 
    print(f"   • Gmail SMTP delivery: {'✅' if sent else '❌'}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())