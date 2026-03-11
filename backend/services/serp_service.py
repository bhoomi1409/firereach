import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def search_google(query: str, num: int = 5) -> list:
    """Real Google search via SerpAPI — deterministic, no LLM guessing"""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "num": num,
        "hl": "en",
        "gl": "us"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        results = data.get("organic_results", [])
        return [r.get("snippet", "") for r in results if r.get("snippet")]
    except Exception as e:
        return [f"Search error: {str(e)}"]

def search_news(company: str) -> list:
    """NewsAPI for recent news about company"""
    if not NEWS_API_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f'"{company}"',
        "apiKey": NEWS_API_KEY,
        "sortBy": "publishedAt",
        "pageSize": 5,
        "language": "en"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        articles = data.get("articles", [])
        return [a.get("title", "") + " — " + a.get("description", "") for a in articles[:5]]
    except Exception:
        return []