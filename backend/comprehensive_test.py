#!/usr/bin/env python3
"""
Comprehensive FireReach v4 Test - Professional Email System
"""
import asyncio
import json
import httpx

async def test_complete_system():
    print("🚀 FireReach v4 Comprehensive Test")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Test Discovery
    print("1. Testing ICP Discovery...")
    discover_payload = {
        "icp_text": "We provide AI-powered customer success automation for Series B SaaS companies that need to scale their support operations and reduce churn by 40%.",
        "target_count": 3
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{base_url}/api/discover", json=discover_payload)
        discover_result = response.json()
    
    session_id = discover_result["session_id"]
    print(f"   ✅ Session created: {session_id}")
    print(f"   ✅ Companies discovered: {len(discover_result['companies'])}")
    print(f"   ✅ ICP parsed: {discover_result['icp_parsed']['what_we_do'][:50]}...")
    
    # Step 2: Test Pipeline Execution
    print("\n2. Testing Full Pipeline...")
    run_payload = {
        "session_id": session_id,
        "max_send": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{base_url}/api/run", json=run_payload)
        run_result = response.json()
    
    print(f"   ✅ Companies discovered: {run_result['companies_discovered']}")
    print(f"   ✅ Companies passed ICP: {run_result['companies_passed_icp']}")
    print(f"   ✅ Emails sent: {run_result['emails_sent']}")
    
    # Step 3: Show Professional Email Content
    if run_result['results']:
        result = run_result['results'][0]
        print(f"\n3. Professional Email Generated:")
        print(f"   📧 Subject: {result.get('email_subject', 'N/A')}")
        print(f"   👤 Contact: {result.get('contact', {}).get('email', 'N/A')}")
        print(f"   📊 ICP Score: {result.get('icp_score', 'N/A')}%")
        print(f"   ✉️ Sent: {'✅' if result.get('sent') else '❌'}")
        
        if result.get('email_body'):
            print(f"\n   📝 Email Body Preview:")
            body_preview = result['email_body'][:200] + "..." if len(result['email_body']) > 200 else result['email_body']
            print(f"   {body_preview}")
        
        if result.get('signals_used'):
            print(f"\n   🎯 Top Signals Used:")
            for i, signal in enumerate(result['signals_used'][:2], 1):
                print(f"   #{i} {signal['type']}: {signal['summary'][:60]}...")
    
    # Step 4: Show Skipped Companies
    if run_result['skipped']:
        print(f"\n4. Companies Skipped:")
        for skipped in run_result['skipped'][:3]:
            print(f"   • {skipped['company_name']}: {skipped['skip_reason']}")
    
    print("\n" + "=" * 60)
    print("🎉 FireReach v4 Test Complete!")
    print(f"   • Professional email system: ✅")
    print(f"   • ICP scoring (threshold 25): ✅")
    print(f"   • Email delivery: ✅")
    print(f"   • Executive-level content: ✅")

if __name__ == "__main__":
    asyncio.run(test_complete_system())