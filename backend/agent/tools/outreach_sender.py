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
    
    body_prompt = f"""Write a hyper-personalized cold email body using these signals and account brief.

{signals_summary}

STRUCTURE:
Paragraph 1: Open with specific signal observation (use exact numbers/names from signals) and its direct business implication
Paragraph 2: Connect to a second signal, explain the hidden risk or opportunity they might not see
Paragraph 3: Value proposition tied to their specific situation with concrete outcome
Paragraph 4: Single clear, low-friction call-to-action question

PERSONALIZATION RULES:
- Reference at least 2-3 specific signals by name/number (e.g., "$300M Series E", "Carlos Santovena", "80 countries")
- Connect signals to their business context (e.g., "With 80-country operations, security complexity grows exponentially")
- Use their company's actual tech/strategy (e.g., "Your AWS infrastructure choice shows...")
- Mention specific roles/people if available in signals
- Tie ICP value prop to their exact growth stage

WRITING RULES:
- NO greeting (start directly with signal observation)
- 150-180 words total
- Professional, peer-to-peer tone (senior consultant to executive)
- Include specific numbers from signals
- End with ONE question that requires minimal effort to answer
- Sign off with just: {sender_name}
- Use proper paragraph breaks (double line breaks)

BANNED PHRASES:
- "Hope this email finds you well"
- "I wanted to reach out"
- "Touch base"
- "Circle back"
- "Hi there" / "Hello"
- "Best regards"

TONE: Knowledgeable peer who's done their homework. Confident, helpful, direct.

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
