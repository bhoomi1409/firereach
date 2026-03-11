"""
tool_signal_harvester — DETERMINISTIC
This tool uses real APIs (SerpAPI, NewsAPI). LLMs must never guess signals.
All data here is API-fetched.
"""
from services.serp_service import search_google, search_news
from models.schemas import SignalData

def tool_signal_harvester(company_name: str) -> SignalData:
    """
    Fetches live buyer signals for a target company.
    
    Searches for:
    - Funding rounds (Series A/B/C, raises)
    - Leadership changes (new CTO, CEO, VP hires)
    - Hiring trends (job postings, headcount growth)
    - Tech stack changes (migrations, new tools)
    - Recent news mentions
    """
    signals = SignalData()
    all_snippets = []
    
    # 1. Funding signals
    funding_results = search_google(f"{company_name} funding round raised Series 2024 2025")
    if funding_results:
        signals.funding_rounds = funding_results[0]
        all_snippets.extend(funding_results)
    
    # 2. Hiring signals
    hiring_results = search_google(f"{company_name} hiring engineers jobs openings 2024 2025")
    if hiring_results:
        signals.hiring_trends = hiring_results[:3]
        all_snippets.extend(hiring_results)
    
    # 3. Leadership changes
    leadership_results = search_google(f"{company_name} new CTO CEO VP appointed joins 2024 2025")
    if leadership_results:
        signals.leadership_changes = leadership_results[0]
        all_snippets.extend(leadership_results)
    
    # 4. Tech stack signals
    tech_results = search_google(f"{company_name} migrated switched technology stack AWS Azure 2024")
    if tech_results:
        signals.tech_stack_changes = tech_results[0]
        all_snippets.extend(tech_results)
    
    # 5. News
    news = search_news(company_name)
    if news:
        signals.news_mentions = news[:3]
        all_snippets.extend(news)
    
    signals.raw_signal_count = len([s for s in all_snippets if s])
    return signals