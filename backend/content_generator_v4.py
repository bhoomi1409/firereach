"""
FireReach — Dual Content Generator v4
ONE Groq call per company → JSON with {email_subject, email_body, brochure_html}

Email:   80 words max, 1-2 signals natural, human tone, one CTA
Brochure: HTML email, 4 sections, personalized per company signals
"""

import os
import json
import html
import httpx
from models import Signal, ParsedICP, GeneratedContent

GROQ_KEY = os.getenv("GROQ_API_KEY", "")

_SYSTEM = """You are a senior executive writing high-level B2B partnership emails. Write professional, executive-caliber outreach that would be appropriate for Fortune 500 communications. Return ONLY valid JSON, no markdown.

Schema:
{
  "email_subject": "Executive subject line under 60 chars, formal business tone",
  "email_body": "Formal executive email, 120-150 words. Professional business language. Reference ONE signal strategically. Clear value proposition. Specific meeting request.",
  "brochure_html": "Executive business proposal HTML with inline CSS"
}

Email Writing Rules:
- Use formal executive language (Dear [Name], I hope this finds you well)
- Reference ONE business signal professionally and strategically
- Present clear, quantified value proposition
- Use industry-appropriate terminology
- End with specific, professional meeting request
- Maintain respectful, peer-to-peer executive tone
- Include proper business email closing

Example Professional Tone:
"Dear [Name],

I hope this message finds you well. I noticed [SPECIFIC SIGNAL] and wanted to reach out regarding a strategic opportunity that aligns with [COMPANY]'s current initiatives.

[COMPANY DESCRIPTION AND VALUE PROP WITH METRICS]

Given [COMPANY]'s focus on [RELEVANT AREA], I believe there's significant potential for collaboration. Our solution has helped similar organizations achieve [SPECIFIC OUTCOME].

Would you be available for a brief 20-minute discussion next week to explore how this might benefit [COMPANY]'s strategic objectives?

Best regards,
[Name]"

Brochure HTML structure (formal executive proposal):
<div style='font-family:"Times New Roman",Times,serif;max-width:700px;margin:0 auto;color:#1a1a1a;background:#ffffff;border:1px solid #e0e0e0'>
  <div style='background:#ffffff;padding:40px 40px 20px;border-bottom:3px solid #2c3e50;text-align:center'>
    <h1 style='color:#2c3e50;margin:0;font-size:32px;font-weight:400;letter-spacing:1px'>STRATEGIC PARTNERSHIP PROPOSAL</h1>
    <div style='width:80px;height:2px;background:#2c3e50;margin:16px auto'></div>
    <p style='color:#666;margin:16px 0 0;font-size:18px;font-style:italic'>Confidential Business Proposal for {{COMPANY_NAME}}</p>
    <p style='color:#999;margin:8px 0 0;font-size:14px'>{{DATE}}</p>
  </div>
  
  <div style='padding:40px;line-height:1.7'>
    <div style='margin-bottom:40px'>
      <h2 style='color:#2c3e50;font-size:22px;margin:0 0 20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Executive Summary</h2>
      <div style='border-left:4px solid #2c3e50;padding-left:20px;margin-bottom:20px'>
        <p style='margin:0;font-size:16px;color:#333'>{{EXECUTIVE_SUMMARY}}</p>
      </div>
    </div>
    
    <div style='margin-bottom:40px'>
      <h2 style='color:#2c3e50;font-size:22px;margin:0 0 20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Market Intelligence & Strategic Context</h2>
      <div style='background:#f8f9fa;padding:20px;border-left:4px solid #007acc;margin-bottom:20px'>
        <p style='margin:0 0 15px;font-size:16px;color:#333'>{{OPPORTUNITY_SECTION}}</p>
        <div style='margin-top:15px'>
          <p style='margin:0;font-size:14px;color:#666;font-style:italic'>Based on current market intelligence and {{COMPANY_NAME}}'s strategic positioning</p>
        </div>
      </div>
    </div>
    
    <div style='margin-bottom:40px'>
      <h2 style='color:#2c3e50;font-size:22px;margin:0 0 20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Projected Business Impact</h2>
      <div style='border:1px solid #e0e0e0;padding:25px;background:#fafafa'>
        <p style='margin:0 0 20px;font-size:16px;color:#333'>{{IMPACT_SECTION}}</p>
        <div style='display:flex;justify-content:space-between;margin-top:20px;padding-top:15px;border-top:1px solid #e0e0e0'>
          <div style='text-align:center;flex:1'>
            <div style='font-size:24px;font-weight:bold;color:#007acc'>Q1</div>
            <div style='font-size:12px;color:#666'>Implementation</div>
          </div>
          <div style='text-align:center;flex:1'>
            <div style='font-size:24px;font-weight:bold;color:#28a745'>40-60%</div>
            <div style='font-size:12px;color:#666'>Efficiency Gain</div>
          </div>
          <div style='text-align:center;flex:1'>
            <div style='font-size:24px;font-weight:bold;color:#dc3545'>ROI</div>
            <div style='font-size:12px;color:#666'>Measurable Impact</div>
          </div>
        </div>
      </div>
    </div>
    
    <div style='background:#2c3e50;color:#ffffff;padding:30px;margin:40px -40px -40px;text-align:center'>
      <h3 style='color:#ffffff;margin:0 0 15px;font-size:20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Recommended Next Steps</h3>
      <p style='margin:0 0 25px;font-size:16px;opacity:0.9'>We recommend scheduling a confidential executive briefing to discuss implementation strategy and partnership terms specific to {{COMPANY_NAME}}'s objectives.</p>
      <div style='margin-top:25px'>
        <a href='{{CALENDAR_LINK}}' style='display:inline-block;background:#ffffff;color:#2c3e50;padding:15px 35px;text-decoration:none;font-weight:600;font-size:16px;text-transform:uppercase;letter-spacing:0.5px;border-radius:0'>Schedule Executive Briefing</a>
      </div>
      <p style='margin:20px 0 0;font-size:12px;opacity:0.7'>This proposal is confidential and intended solely for {{COMPANY_NAME}} executive review</p>
    </div>
  </div>
</div>"""

async def generate_content(
    company: dict,
    contact: dict,
    signals: list[Signal],
    icp: ParsedICP,
    calendar_link: str = "https://cal.com/your-link"
) -> GeneratedContent:
    """
    One Groq call → email + brochure for this company.
    Returns GeneratedContent with both fields populated.
    """
    fname       = contact.get("first_name", "there") if isinstance(contact, dict) else "there"
    top3        = signals[:3]
    signals_str = "\n".join([f"- {s.summary}" for s in top3])

    user_prompt = f"""Generate professional B2B outreach content for:

Company: {company.get('name')}
Industry: {company.get('industry', icp.target_industry)}
Contact: {fname} {contact.get('last_name', '')} — {contact.get('title','') if isinstance(contact, dict) else ''}
Our service: {icp.what_we_do}
Their business challenge: {icp.pain_keyword}
Our solution: {icp.solution_keyword}
Key business signals:
{signals_str}
Calendar link: {calendar_link}

Write a professional executive-level email (100 words max) and comprehensive business proposal brochure HTML. Use formal business language appropriate for C-level executives."""

    try:
        async with httpx.AsyncClient(timeout=25) as c:
            r = await c.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": _SYSTEM},
                        {"role": "user",   "content": user_prompt}
                    ],
                    "max_tokens": 1200,
                    "temperature": 0.7
                }
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown fences
        FENCE = chr(96)*3
        if raw.startswith(FENCE):
            raw = raw.split(FENCE)[1]
            if raw.startswith("json"): raw = raw[4:]
        data = json.loads(raw)
        return GeneratedContent(
            email_subject = data.get("email_subject", f"Quick question for {company.get('name')}"),
            email_body    = data.get("email_body", _fallback_email(company, fname, top3, icp)),
            brochure_html = data.get("brochure_html", _fallback_brochure(company, icp, top3)),
        )

    except Exception as e:
        return GeneratedContent(
            email_subject = f"Quick question for {company.get('name', '')}",
            email_body    = _fallback_email(company, fname, top3, icp),
            brochure_html = _fallback_brochure(company, icp, top3),
        )

def _fallback_email(company: dict, fname: str, signals: list[Signal], icp: ParsedICP) -> str:
    company_name = company.get('name', 'your organization')
    signal = signals[0].summary if signals else "your organization's recent strategic initiatives"
    
    return f"""Dear {fname},

I hope this message finds you well. I noticed {signal} and wanted to reach out regarding a strategic partnership opportunity that aligns with {company_name}'s current business objectives.

{icp.what_we_do} We have a proven track record of helping organizations like {company_name} address critical challenges in {icp.pain_keyword}, delivering measurable results through {icp.solution_keyword}.

Given {company_name}'s focus on growth and operational excellence, I believe there is significant potential for collaboration. Our clients typically see substantial improvements in efficiency and cost reduction within the first quarter of implementation.

Would you be available for a brief 20-minute executive discussion next week to explore how this partnership could specifically benefit {company_name}'s strategic initiatives?

I look forward to the opportunity to connect.

Best regards,
[Your Name]
[Your Title]
[Your Company]"""

def _fallback_brochure(company: dict, icp: ParsedICP, signals: list[Signal]) -> str:
    company_name = html.escape(company.get('name', 'Your Company'))  # Sanitize HTML
    sig_html = "".join(f"<li style='margin-bottom:12px;font-size:15px;color:#333'>{html.escape(s.summary)}</li>" for s in signals[:3])
    
    return f"""<div style='font-family:"Times New Roman",Times,serif;max-width:700px;margin:0 auto;color:#1a1a1a;background:#ffffff;border:1px solid #e0e0e0'>
  <div style='background:#ffffff;padding:40px 40px 20px;border-bottom:3px solid #2c3e50;text-align:center'>
    <h1 style='color:#2c3e50;margin:0;font-size:32px;font-weight:400;letter-spacing:1px'>STRATEGIC PARTNERSHIP PROPOSAL</h1>
    <div style='width:80px;height:2px;background:#2c3e50;margin:16px auto'></div>
    <p style='color:#666;margin:16px 0 0;font-size:18px;font-style:italic'>Confidential Business Proposal for {company_name}</p>
    <p style='color:#999;margin:8px 0 0;font-size:14px'>March 2026</p>
  </div>
  
  <div style='padding:40px;line-height:1.7'>
    <div style='margin-bottom:40px'>
      <h2 style='color:#2c3e50;font-size:22px;margin:0 0 20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Executive Summary</h2>
      <div style='border-left:4px solid #2c3e50;padding-left:20px;margin-bottom:20px'>
        <p style='margin:0;font-size:16px;color:#333'>Based on comprehensive market analysis and {company_name}'s current strategic positioning, we have identified a significant opportunity for operational enhancement through {html.escape(icp.solution_keyword)}. This proposal outlines a strategic partnership framework designed to address critical business challenges while delivering measurable ROI within the first implementation quarter.</p>
      </div>
    </div>
    
    <div style='margin-bottom:40px'>
      <h2 style='color:#2c3e50;font-size:22px;margin:0 0 20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Market Intelligence & Strategic Context</h2>
      <div style='background:#f8f9fa;padding:20px;border-left:4px solid #007acc;margin-bottom:20px'>
        <p style='margin:0 0 15px;font-size:16px;color:#333'>Our analysis of {company_name}'s market position reveals several strategic opportunities aligned with current industry trends in {html.escape(icp.target_industry)}:</p>
        <ul style='margin:15px 0;padding-left:25px'>{sig_html}</ul>
        <div style='margin-top:15px'>
          <p style='margin:0;font-size:14px;color:#666;font-style:italic'>Based on current market intelligence and {company_name}'s strategic positioning</p>
        </div>
      </div>
    </div>
    
    <div style='margin-bottom:40px'>
      <h2 style='color:#2c3e50;font-size:22px;margin:0 0 20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Projected Business Impact</h2>
      <div style='border:1px solid #e0e0e0;padding:25px;background:#fafafa'>
        <p style='margin:0 0 20px;font-size:16px;color:#333'>{html.escape(icp.what_we_do)} Our proven methodology has consistently delivered transformational results for organizations similar to {company_name}, with clients typically experiencing substantial improvements in operational efficiency, cost optimization, and strategic capability enhancement within the first quarter of engagement.</p>
        <div style='display:flex;justify-content:space-between;margin-top:20px;padding-top:15px;border-top:1px solid #e0e0e0'>
          <div style='text-align:center;flex:1'>
            <div style='font-size:24px;font-weight:bold;color:#007acc'>Q1</div>
            <div style='font-size:12px;color:#666'>Implementation</div>
          </div>
          <div style='text-align:center;flex:1'>
            <div style='font-size:24px;font-weight:bold;color:#28a745'>40-60%</div>
            <div style='font-size:12px;color:#666'>Efficiency Gain</div>
          </div>
          <div style='text-align:center;flex:1'>
            <div style='font-size:24px;font-weight:bold;color:#dc3545'>ROI</div>
            <div style='font-size:12px;color:#666'>Measurable Impact</div>
          </div>
        </div>
      </div>
    </div>
    
    <div style='background:#2c3e50;color:#ffffff;padding:30px;margin:40px -40px -40px;text-align:center'>
      <h3 style='color:#ffffff;margin:0 0 15px;font-size:20px;font-weight:400;text-transform:uppercase;letter-spacing:0.5px'>Recommended Next Steps</h3>
      <p style='margin:0 0 25px;font-size:16px;opacity:0.9'>We recommend scheduling a confidential executive briefing to discuss implementation strategy and partnership terms specific to {company_name}'s objectives.</p>
      <div style='margin-top:25px'>
        <a href='https://cal.com/your-link' style='display:inline-block;background:#ffffff;color:#2c3e50;padding:15px 35px;text-decoration:none;font-weight:600;font-size:16px;text-transform:uppercase;letter-spacing:0.5px;border-radius:0'>Schedule Executive Briefing</a>
      </div>
      <p style='margin:20px 0 0;font-size:12px;opacity:0.7'>This proposal is confidential and intended solely for {company_name} executive review</p>
    </div>
  </div>
</div>"""