"""
tool_research_analyst — AI TOOL
Takes harvested signals + ICP, returns a 2-paragraph Account Brief.
"""
from models.schemas import SignalData
from services.llm_service import call_llm
from agent.prompts import RESEARCH_ANALYST_PROMPT
import json

def tool_research_analyst(signals: SignalData, icp: str) -> str:
    """
    Synthesizes live signals with the seller's ICP.
    Returns a 2-paragraph Account Brief.
    """
    signals_text = f"""
COMPANY SIGNALS:
- Funding: {signals.funding_rounds or 'Not found'}
- Leadership Changes: {signals.leadership_changes or 'Not found'}
- Hiring Trends: {', '.join(signals.hiring_trends) if signals.hiring_trends else 'Not found'}
- Tech Stack: {signals.tech_stack_changes or 'Not found'}
- Recent News: {'; '.join(signals.news_mentions[:2]) if signals.news_mentions else 'Not found'}
- Headcount: {signals.headcount_growth or 'Not found'}

SELLER ICP:
{icp}
"""
    brief = call_llm(
        system_prompt=RESEARCH_ANALYST_PROMPT,
        user_message=signals_text,
        temperature=0.4,
        max_tokens=300
    )
    return brief