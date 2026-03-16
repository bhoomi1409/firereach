"""
FireReach — Company Enrichment v4
Deep enrichment using multiple data sources
"""

import os
import asyncio
import httpx
from typing import Dict, Any

HUNTER_KEY = os.getenv("HUNTER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

async def enrich_company(company_name: str, domain_hint: str = "") -> Dict[str, Any]:
    """
    Enrich company data using multiple sources.
    Returns comprehensive company profile.
    """
    company = {
        "name": company_name,
        "domain": domain_hint or f"{company_name.lower().replace(' ', '')}.com",
        "description": f"{company_name} - Technology company",
        "industry": "technology",
        "headcount": 150,  # Default estimate
        "funding": "series_b",
        "keywords": ["technology", "software", "innovation"],
        "web_snippets": [],
        "hunter_emails": [],
        "news": []
    }
    
    # Parallel enrichment from multiple sources
    tasks = []
    
    if HUNTER_KEY and len(HUNTER_KEY) > 10:
        tasks.append(enrich_with_hunter(company_name, company["domain"]))
    
    if NEWS_API_KEY and len(NEWS_API_KEY) > 10:
        tasks.append(enrich_with_news(company_name))
    
    # Run enrichment tasks in parallel
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                company.update(result)
    
    return company

async def enrich_with_hunter(company_name: str, domain: str) -> Dict[str, Any]:
    """Enrich using Hunter.io domain search."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(
                "https://api.hunter.io/v2/domain-search",
                params={
                    "domain": domain,
                    "api_key": HUNTER_KEY,
                    "limit": 10
                }
            )
            response.raise_for_status()
            data = response.json()
            
            emails = data.get("data", {}).get("emails", [])
            organization = data.get("data", {}).get("organization", {})
            
            return {
                "hunter_emails": emails[:5],  # Top 5 emails
                "description": organization.get("description", ""),
                "industry": organization.get("industry", "technology"),
                "headcount": organization.get("headcount", 150)
            }
    except Exception:
        return {}

async def enrich_with_news(company_name: str) -> Dict[str, Any]:
    """Enrich using NewsAPI for recent mentions."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": f'"{company_name}"',
                    "apiKey": NEWS_API_KEY,
                    "sortBy": "publishedAt",
                    "pageSize": 5,
                    "language": "en"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            news_items = []
            
            for article in articles[:3]:
                news_items.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", "")
                })
            
            return {"news": news_items}
    except Exception:
        return {}