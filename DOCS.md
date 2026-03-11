# FireReach — DOCS.md

## Agent Logic Flow

1. User submits ICP + target company + recipient email via dashboard
2. FastAPI receives request at POST /api/outreach
3. Orchestrator enforces sequential tool execution:
   - tool_signal_harvester: Calls SerpAPI + NewsAPI for live signals (zero LLM involvement)
   - tool_research_analyst: Passes signals + ICP to Llama 3.3 70B → 2-paragraph Account Brief
   - tool_outreach_automated_sender: Generates personalized email → auto-dispatches via Resend
4. Response (signals + brief + email + log) returned to frontend dashboard

## How Outreach is Grounded in Signals

- tool_signal_harvester returns only real API data. LLM cannot modify or fabricate it.
- EMAIL_WRITER_PROMPT explicitly instructs the LLM to cite ≥2 specific signals.
- If no signals are found, the pipeline halts — no email is sent.

## Tool Schemas

### tool_signal_harvester
- Input: { company_name: string }
- Output: SignalData (funding_rounds, leadership_changes, hiring_trends, tech_stack_changes, news_mentions)
- Type: DETERMINISTIC — SerpAPI + NewsAPI only

### tool_research_analyst
- Input: { signals: SignalData, icp: string }
- Output: string (2-paragraph Account Brief)
- Type: AI — Groq Llama 3.3 70B

### tool_outreach_automated_sender
- Input: { account_brief, signals, recipient_email, sender_name, icp }
- Output: { subject, body, sent, send_message }
- Type: AI + Execution — generates email + calls Resend/SMTP

## System Prompt

### Agent Persona
You are FireReach, an elite Autonomous Outreach Agent built for GTM teams. You think like a senior SDR with 10+ years of outbound experience. You never write generic emails. Every message you send must be grounded in specific, real-time data that was fetched for you by live tools.

### Constraints
1. ALWAYS follow exact sequence: tool_signal_harvester → tool_research_analyst → tool_outreach_automated_sender
2. NEVER skip a step or change the order
3. NEVER hallucinate signals — only use data from tool_signal_harvester
4. ZERO TEMPLATE POLICY: Email must cite ≥2 specific signals
5. Do NOT send email until tool_research_analyst has returned Account Brief
6. Subject line must include company name + one specific signal
7. Max email length: 150 words
8. Tone: Peer-level, confident, not salesy
9. End with ONE low-friction CTA only
10. NEVER use: "Hope this finds you well", "I wanted to reach out", "touch base"

## Deployment

### Backend: Render
- Root: backend/
- Build command: pip install -r requirements.txt
- Start command: uvicorn main:app --host 0.0.0.0 --port 8000
- Environment variables: GROQ_API_KEY, SERP_API_KEY, NEWS_API_KEY, RESEND_API_KEY, SENDER_EMAIL

### Frontend: Vercel
- Root: frontend/
- Framework: Next.js
- Environment variable: NEXT_PUBLIC_API_URL=https://your-app.onrender.com

## API Endpoints

### GET /health
Returns service status for health checks.

### POST /api/outreach
Main endpoint that triggers the 3-tool agentic pipeline.

**Request Body:**
```json
{
  "icp": "We sell cybersecurity training to Series B startups",
  "target_company": "Deel",
  "recipient_email": "cto@deel.com",
  "sender_name": "Alex"
}
```

**Response:**
```json
{
  "success": true,
  "signals": {
    "funding_rounds": "Deel raised $425M Series D...",
    "leadership_changes": "New VP of Engineering hired...",
    "hiring_trends": ["Hiring 50+ engineers", "Remote-first expansion"],
    "tech_stack_changes": "Migrated to microservices...",
    "news_mentions": ["Deel expands to APAC", "New compliance features"],
    "raw_signal_count": 8
  },
  "account_brief": "Deel recently secured $425M in Series D funding and is aggressively hiring 50+ engineers across their platform team. This rapid expansion, combined with their move to microservices architecture, indicates they're scaling their infrastructure to handle increased transaction volume and regulatory complexity.\n\nThis growth trajectory creates immediate cybersecurity risks as their attack surface expands with new hires and distributed systems. Their Series B stage aligns perfectly with companies that need enterprise-grade security training to protect against insider threats and ensure compliance across multiple jurisdictions.",
  "email_subject": "Deel's $425M raise + 50 new engineers = security priority?",
  "email_body": "Alex,\n\nNoticed Deel just closed $425M Series D and you're hiring 50+ engineers. That's impressive growth, but also means your attack surface is expanding rapidly.\n\nWith new team members accessing sensitive financial data and your recent microservices migration, insider threat training becomes critical. We've helped other Series B fintech companies like yours reduce security incidents by 73% during rapid scaling phases.\n\nWorth a 15-min conversation about protecting Deel's growth trajectory?",
  "send_status": true,
  "send_message": "Sent via Resend to cto@deel.com",
  "execution_log": [
    "🔍 Step 1: tool_signal_harvester — Fetching live buyer signals...",
    "✅ Signals captured: 8 signals found.",
    "   → Funding: Found",
    "   → Hiring: 2 signals",
    "   → News: 3 mentions",
    "🧠 Step 2: tool_research_analyst — Generating Account Brief...",
    "✅ Account Brief generated.",
    "📧 Step 3: tool_outreach_automated_sender — Drafting and dispatching email...",
    "✅ Sent via Resend to cto@deel.com"
  ]
}
```

## Error Handling

The system includes comprehensive error handling:

1. **No Signals Found**: If raw_signal_count = 0, pipeline halts with appropriate message
2. **API Failures**: SerpAPI/NewsAPI failures return mock data with warnings
3. **LLM Failures**: JSON parsing errors fall back to raw output
4. **Email Failures**: Resend failures automatically fall back to SMTP
5. **Validation**: Input validation for required fields

## Testing Checklist

### The Rabbitt Challenge Test
Test with exactly:
- ICP: "We sell high-end cybersecurity training to Series B startups."
- Target Company: "Deel" (or any recently-funded startup)
- Recipient: your-candidate-email@gmail.com

Expected output:
- At least 3 real signals fetched
- Account Brief correctly connects signals to cybersecurity training need
- Email subject contains company name + a specific signal
- Email body cites ≥2 signals explicitly
- Email actually arrives in inbox

### Development Setup

1. **Backend Setup:**
   ```bash
   cd firereach/backend
   pip install -r requirements.txt
   cp .env.example .env
   # Add your API keys to .env
   uvicorn main:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd firereach/frontend
   npm install
   cp .env.local.example .env.local
   # Set NEXT_PUBLIC_API_URL=http://localhost:8000
   npm run dev
   ```

3. **Test Health Endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

## Production Considerations

1. **Rate Limiting**: SerpAPI free tier = 100 searches/month
2. **Error Recovery**: Mock signals returned when API quota exceeded
3. **Security**: All API keys via environment variables
4. **CORS**: Properly configured for frontend origin
5. **Logging**: Comprehensive execution logs for debugging
6. **Validation**: Input sanitization and email validation

## Architecture Decisions

1. **Sequential Tool Execution**: Enforced by orchestrator to ensure data integrity
2. **Deterministic Signal Harvesting**: No LLM involvement in data collection
3. **Auto-Send**: No human approval required for true automation
4. **Fallback Systems**: SMTP fallback for email, mock data for API failures
5. **Stateless Design**: Each request is independent, results stored client-side