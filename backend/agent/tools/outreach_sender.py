"""
tool_outreach_automated_sender — AI + EXECUTION TOOL
Generates personalized email and dispatches it automatically.
Agent triggers this ONLY after receiving the Account Brief.
"""
from models.schemas import SignalData
from services.llm_service import call_llm
from services.email_service import send_email
from agent.prompts import AGENT_SYSTEM_PROMPT

def tool_outreach_automated_sender(
    account_brief: str,
    signals: SignalData,
    recipient_email: str,
    sender_name: str,
    icp: str
) -> dict:
    """
    1. Generates hyper-personalized email from Account Brief + signals
    2. Automatically dispatches it via Gmail SMTP
    Returns: {subject, body, sent, send_message}
    """
    
    # Get top signal for subject line
    top_signal = None
    company_name = "the company"
    
    if signals.funding_rounds:
        top_signal = signals.funding_rounds[:100]
    elif signals.hiring_trends and len(signals.hiring_trends) > 0:
        top_signal = signals.hiring_trends[0][:100]
    elif signals.news_mentions and len(signals.news_mentions) > 0:
        top_signal = signals.news_mentions[0][:100]
    else:
        top_signal = "recent growth signals"
    
    # Extract company name from signals if possible
    if signals.funding_rounds:
        words = signals.funding_rounds.split()
        for word in words[:5]:
            if word[0].isupper() and len(word) > 3:
                company_name = word.strip(".,")
                break
    
    # CALL 1: Generate subject line only
    subject_prompt = f"""Write a cold email subject line for {company_name} referencing this signal: {top_signal}. 
Include company name. Max 10 words. Return subject line only. No quotes. No extra text."""
    
    subject = call_llm(
        system_prompt="You are a B2B email subject line expert. Return only the subject line, nothing else.",
        user_message=subject_prompt,
        temperature=0.7,
        max_tokens=50
    ).strip().strip('"').strip("'")
    
    # CALL 2: Generate email body only
    signals_summary = f"""
SIGNALS:
- Funding: {signals.funding_rounds or 'N/A'}
- Hiring: {', '.join(signals.hiring_trends[:2]) if signals.hiring_trends else 'N/A'}
- Leadership: {signals.leadership_changes or 'N/A'}
- Tech: {signals.tech_stack_changes or 'N/A'}
- News: {signals.news_mentions[0] if signals.news_mentions else 'N/A'}

ACCOUNT BRIEF:
{account_brief}

SELLER ICP:
{icp}
"""
    
    body_prompt = f"""Write a professional cold email body using these signals and account brief.

{signals_summary}

STRUCTURE:
Paragraph 1: Open with specific signal observation and its business implication
Paragraph 2: Connect to pain point with another signal, explain the risk/opportunity
Paragraph 3: Value proposition with specific outcome or proof point
Paragraph 4: Single clear call-to-action

RULES:
- Start with "Hi there," (professional greeting)
- 3-4 paragraphs, 180-200 words total
- Cite 2-3 specific signals with context
- Professional, consultative tone (peer-to-peer, not salesy)
- Include specific numbers or outcomes when possible
- End with ONE clear, low-friction question
- Sign off with: {sender_name}
- Use proper paragraph breaks (double line breaks)
- NO "Best regards", NO "Hope this email finds you well"

TONE: Senior consultant speaking to peer executive. Knowledgeable, helpful, direct.

Return plain email text only. No JSON. No subject line. No formatting markers."""
    
    body = call_llm(
        system_prompt=AGENT_SYSTEM_PROMPT,
        user_message=body_prompt,
        temperature=0.6,
        max_tokens=500
    ).strip()
    
    # Clean up body if needed
    if body.startswith('"') or body.startswith("'"):
        body = body.strip('"').strip("'")
    
    # AUTO-SEND (agent-triggered, no human confirmation)
    send_result = send_email(
        to_email=recipient_email,
        subject=subject,
        body=body
    )
    
    return {
        "subject": subject,
        "body": body,
        "sent": send_result["sent"],
        "send_message": send_result["message"]
    }
