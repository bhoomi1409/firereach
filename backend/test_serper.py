#!/usr/bin/env python3
"""
Test Serper API directly
"""
import os
import httpx
import asyncio

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

async def test_serper():
    serper_key = os.getenv("SERP_API_KEY", "")
    print(f"Serper API Key: {serper_key[:10]}...{serper_key[-5:] if serper_key else 'None'}")
    
    if not serper_key:
        print("❌ No Serper API key found")
        return
    
    query = "saas companies series b funding 2024 site:techcrunch.com"
    print(f"Testing query: {query}")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                json={"q": query, "num": 5}
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Serper API working!")
            print(f"Results found: {len(data.get('organic', []))}")
            
            for i, result in enumerate(data.get('organic', [])[:3], 1):
                print(f"{i}. {result.get('title', 'No title')}")
                print(f"   {result.get('link', 'No link')}")
                
    except Exception as e:
        print(f"❌ Serper API error: {e}")

if __name__ == "__main__":
    asyncio.run(test_serper())