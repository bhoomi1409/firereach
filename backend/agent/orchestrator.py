"""
Core agent orchestrator — enforces strict 3-step sequential tool execution:
Step 1: tool_signal_harvester (deterministic, API-based)
Step 2: tool_research_analyst (AI synthesis)
Step 3: tool_outreach_automated_sender (AI generation + auto-send)

The agent CANNOT skip steps or reorder them.
"""
import logging
from models.schemas import SignalData, OutreachResponse
from agent.tools.signal_harvester import tool_signal_harvester
from agent.tools.research_analyst import tool_research_analyst
from agent.tools.outreach_sender import tool_outreach_automated_sender

logger = logging.getLogger(__name__)

async def run_firereach_agent(
    icp: str,
    target_company: str,
    recipient_email: str,
    sender_name: str = "Alex"
) -> OutreachResponse:
    """
    Autonomous agent that executes the full outreach pipeline.
    Sequential: Signal Capture → Account Research → Automated Delivery
    """
    log = []
    
    try:
        # ─── STEP 1: SIGNAL HARVESTING (DETERMINISTIC) ───────────────────────
        log.append("🔍 Step 1: tool_signal_harvester — Fetching live buyer signals...")
        logger.info(f"Harvesting signals for: {target_company}")
        
        signals: SignalData = tool_signal_harvester(company_name=target_company)
        
        if signals.raw_signal_count == 0:
            log.append("⚠️  No signals found. Cannot proceed with outreach.")
            return OutreachResponse(
                success=False,
                signals=signals,
                account_brief="",
                email_subject="",
                email_body="",
                send_status=False,
                send_message="Halted: No live signals found for this company.",
                execution_log=log,
                error="No signals found"
            )
        
        log.append(f"✅ Signals captured: {signals.raw_signal_count} signals found.")
        log.append(f"   → Funding: {'Found' if signals.funding_rounds else 'None'}")
        log.append(f"   → Hiring: {len(signals.hiring_trends)} signals")
        log.append(f"   → News: {len(signals.news_mentions)} mentions")
        
        # ─── STEP 2: ACCOUNT RESEARCH (AI) ───────────────────────────────────
        log.append("🧠 Step 2: tool_research_analyst — Generating Account Brief...")
        
        account_brief: str = tool_research_analyst(signals=signals, icp=icp)
        
        if not account_brief or len(account_brief.strip()) < 20:
            log.append("⚠️  Account Brief generation failed.")
            return OutreachResponse(
                success=False,
                signals=signals,
                account_brief="",
                email_subject="",
                email_body="",
                send_status=False,
                send_message="Failed to generate Account Brief",
                execution_log=log,
                error="Research analyst failed"
            )
        
        log.append("✅ Account Brief generated.")
        
        # ─── STEP 3: EMAIL GENERATION + AUTO-SEND ────────────────────────────
        log.append("📧 Step 3: tool_outreach_automated_sender — Drafting and dispatching email...")
        
        email_result = tool_outreach_automated_sender(
            account_brief=account_brief,
            signals=signals,
            recipient_email=recipient_email,
            sender_name=sender_name,
            icp=icp
        )
        
        status_icon = "✅" if email_result["sent"] else "⚠️"
        log.append(f"{status_icon} {email_result['send_message']}")
        
        return OutreachResponse(
            success=True,
            signals=signals,
            account_brief=account_brief,
            email_subject=email_result["subject"],
            email_body=email_result["body"],
            send_status=email_result["sent"],
            send_message=email_result["send_message"],
            execution_log=log
        )
    
    except Exception as e:
        logger.error(f"Agent failed: {str(e)}")
        log.append(f"❌ Agent error: {str(e)}")
        return OutreachResponse(
            success=False,
            signals=SignalData(),
            account_brief="",
            email_subject="",
            email_body="",
            send_status=False,
            send_message="Agent encountered an error",
            execution_log=log,
            error=str(e)
        )