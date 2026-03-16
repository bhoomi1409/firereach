#!/usr/bin/env python3
"""
FireReach v4 System Test
Tests the complete pipeline end-to-end
"""

import sys
import os
import asyncio
sys.path.append('firereach/backend')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('firereach/backend/.env')
    print("✅ Environment loaded")
except ImportError:
    print("❌ dotenv not available")

async def test_firereach_system():
    print("\n=== FIREREACH v4 SYSTEM TEST ===\n")
    
    # Test 1: Environment Variables
    print("1. Testing Environment Variables:")
    env_vars = ['GROQ_API_KEY', 'SMTP_USER', 'SMTP_APP_PASSWORD', 'SERP_API_KEY']
    all_env_ok = True
    for var in env_vars:
        value = os.getenv(var, '')
        if value:
            print(f"   ✅ {var}: {value[:10]}...")
        else:
            print(f"   ❌ {var}: Not set")
            all_env_ok = False
    
    if not all_env_ok:
        print("\n❌ Environment variables missing. Please check .env file.")
        return False
    
    # Test 2: Module Imports
    print("\n2. Testing Module Imports:")
    try:
        from models.v4_models import ParsedICP, DiscoveredCompany, CompanyResult
        from icp_parser import parse_icp
        from company_discovery_v4 import discover_companies
        from icp_scorer_v4 import score_company
        from enrichment_v4 import enrich_company
        from signal_engine_v4 import extract_signals
        from contact_finder_v4 import find_contact
        from content_generator_v4 import generate_content
        from email_sender_v4 import send_with_brochure
        print("   ✅ All modules imported successfully")
    except Exception as e:
        print(f"   ❌ Module import failed: {e}")
        return False
    
    # Test 3: ICP Parsing
    print("\n3. Testing ICP Parsing:")
    try:
        icp_text = "We build AI voice agents for Series B fintech companies. They struggle with scaling customer support and need to reduce call times by 60%."
        icp = await parse_icp(icp_text)
        print(f"   ✅ ICP parsed: {icp.what_we_do}")
        print(f"   ✅ Industry: {icp.target_industry}")
        print(f"   ✅ Threshold: {icp.threshold}")
    except Exception as e:
        print(f"   ❌ ICP parsing failed: {e}")
        return False
    
    # Test 4: Company Discovery
    print("\n4. Testing Company Discovery:")
    try:
        companies = await discover_companies(icp, target_count=3)
        print(f"   ✅ Discovered {len(companies)} companies")
        for i, company in enumerate(companies[:2]):
            print(f"   ✅ Company {i+1}: {company.name} ({company.domain})")
    except Exception as e:
        print(f"   ❌ Company discovery failed: {e}")
        return False
    
    # Test 5: Company Enrichment
    print("\n5. Testing Company Enrichment:")
    try:
        if companies:
            company_data = await enrich_company(companies[0].name, companies[0].domain)
            print(f"   ✅ Enriched: {company_data['name']}")
            print(f"   ✅ Domain: {company_data['domain']}")
            print(f"   ✅ Industry: {company_data['industry']}")
    except Exception as e:
        print(f"   ❌ Company enrichment failed: {e}")
        return False
    
    # Test 6: ICP Scoring
    print("\n6. Testing ICP Scoring:")
    try:
        score, reason, proceed = score_company(company_data, icp)
        print(f"   ✅ ICP Score: {score}% ({reason})")
        print(f"   ✅ Should proceed: {proceed}")
    except Exception as e:
        print(f"   ❌ ICP scoring failed: {e}")
        return False
    
    # Test 7: Signal Extraction
    print("\n7. Testing Signal Extraction:")
    try:
        signals = extract_signals(company_data, icp)
        print(f"   ✅ Extracted {len(signals)} signals")
        if signals:
            print(f"   ✅ Top signal: {signals[0].summary[:60]}...")
    except Exception as e:
        print(f"   ❌ Signal extraction failed: {e}")
        return False
    
    # Test 8: Contact Finding
    print("\n8. Testing Contact Finding:")
    try:
        contact = await find_contact(company_data, icp.buyer_titles)
        print(f"   ✅ Contact found: {contact.email}")
        print(f"   ✅ Source: {contact.source}")
    except Exception as e:
        print(f"   ❌ Contact finding failed: {e}")
        return False
    
    # Test 9: Content Generation
    print("\n9. Testing Content Generation:")
    try:
        content = await generate_content(
            company_data, contact.model_dump(), signals[:3], icp
        )
        print(f"   ✅ Email subject: {content.email_subject}")
        print(f"   ✅ Email body length: {len(content.email_body)} chars")
        print(f"   ✅ Brochure length: {len(content.brochure_html)} chars")
    except Exception as e:
        print(f"   ❌ Content generation failed: {e}")
        return False
    
    # Test 10: Email Sending (Dry Run)
    print("\n10. Testing Email Sending (Dry Run):")
    try:
        log = []
        # Test with a safe email that won't actually send
        sent = send_with_brochure(
            "test@example.com",  # Safe test email
            content.email_subject,
            content.email_body,
            content.brochure_html,
            company_data['name'],
            log
        )
        print(f"   ✅ Email send attempted: {sent}")
        print(f"   ✅ Log: {log[-1] if log else 'No log'}")
    except Exception as e:
        print(f"   ❌ Email sending failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED! FireReach v4 is working correctly.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_firereach_system())
    if success:
        print("\n✅ System is ready for production use!")
    else:
        print("\n❌ System has issues that need to be fixed.")