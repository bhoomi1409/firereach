# FireReach — Technical Documentation

## Agent Logic Flow

```
User Input (ICP + Company + Email)
          ↓
POST /api/outreach (FastAPI)
          ↓
┌─── Orchestrator ───────────────────────────────┐
│                                                 │
│  1. tool_signal_harvester (DETERMINISTIC)      │
│     → SerpAPI: 4 targeted Google searches      │
│     → NewsAPI: recent company news             │
│     → Returns: SignalData JSON                 │
│     → If raw_signal_count == 0: HALT           │
│                                                 │
│  2. tool_research_analyst (AI)                 │
│     → Input: SignalData + ICP                  │
│     → Groq Llama 3.3 70B (temp: 0.4)           │
│     → Output: 2-paragraph Account Brief        │
│     → Max 120 words, no fluff                  │
│                                                 │
│  3. tool_outreach_automated_sender (AI+ACTION) │
│     → Input: Brief + Signals + ICP             │
│     → Groq Llama 3.3 70B (temp: 0.6)           │
│     → Generates subject + body separately      │
│     → Gmail SMTP auto-sends                    │
│     → Returns send status                      │
│                                                 │
└─────────────────────────────────────────────────┘
          ↓
OutreachResponse → Next.js Dashboard
```

---

## How Outreach Stays Grounded in Signals

| Rule | Implementation |
|------|----------------|
| No hallucinated signals | signal_harvester uses only SerpAPI + NewsAPI — LLM never touches raw data collection |
| ≥2 signals cited in email | EMAIL_WRITER_PROMPT explicitly instructs LLM to reference exact signals by name/number |
| Pipeline halts if no data | `if raw_signal_count == 0: return error` in orchestrator |
| Zero template policy | Prompt bans "Hope this finds you well", "touch base", generic openers |

---

## Tool Schemas

### tool_signal_harvester

```json
{
  "name": "tool_signal_harvester",
  "type": "DETERMINISTIC — SerpAPI + NewsAPI, zero LLM",
  "input": {
    "company_name": "string"
  },
  "output": {
    "funding_rounds": "string | null",
    "leadership_changes": "string | null",
    "hiring_trends": "string[]",
    "tech_stack_changes": "string | null",
    "news_mentions": "string[]",
    "raw_signal_count": "int"
  }
}
```

### tool_research_analyst

```json
{
  "name": "tool_research_analyst",
  "type": "AI — Groq Llama 3.3 70B",
  "input": {
    "signals": "SignalData",
    "icp": "string"
  },
  "output": "string (2-paragraph Account Brief, max 120 words)"
}
```

### tool_outreach_automated_sender

```json
{
  "name": "tool_outreach_automated_sender",
  "type": "AI + Execution — Groq + Gmail SMTP",
  "input": {
    "account_brief": "string",
    "signals": "SignalData",
    "recipient_email": "string",
    "sender_name": "string",
    "icp": "string"
  },
  "output": {
    "subject": "string",
    "body": "string",
    "sent": "boolean",
    "send_message": "string"
  }
}
```

---

## System Prompt

### Agent Persona

You are FireReach, an elite Autonomous Outreach Agent for GTM teams. You think like a senior SDR with 10+ years of outbound experience. Every message must be grounded in specific real-time data from tools.

### Constraints

1. **Sequence**: signal_harvester → research_analyst → outreach_sender (never reorder)
2. **Never hallucinate signals** — only use data from tool_signal_harvester
3. **Zero Template Policy** — cite ≥2 specific signals in every email
4. **No send until Account Brief is ready**
5. **Subject**: company name + one specific signal
6. **Body**: max 180 words
7. **Tone**: peer-level, confident, not salesy
8. **End with exactly one low-friction CTA** (a question)
9. **Banned phrases**: "Hope this finds you well", "touch base", "circle back", "Hi there", "I wanted to reach out"

### Email Format

```
[Specific signal observation — no greeting]

[Connect signal to risk/pain — 1-2 sentences]

[Value proposition — 1 sentence]

[CTA question]

— [Sender Name]
```

---

## Evaluation Rubric Coverage

| Category | Requirement | How FireReach Covers It |
|----------|-------------|-------------------------|
| **Tool Chaining** | Signal → Research → Send | Orchestrator enforces strict sequential execution, halts on failure |
| **Outreach Quality** | Human-like, cites live data | Zero-template prompt + signal-grounded generation with ≥2 specific citations |
| **Automation Flow** | Mail tool triggers with right context | tool_outreach_automated_sender called only after Account Brief ready |
| **UI/UX + Docs** | Clear output, documented loop | Mission Control dashboard + this DOCS.md |

---

## Personalization Strategy

FireReach achieves hyper-personalization through:

1. **Signal Specificity**: References exact numbers, names, and dates from harvested data
   - Example: "$300M Series E" not "recent funding"
   - Example: "Carlos Santovena as VP Operations" not "new hire"

2. **Context Mapping**: Connects signals to business implications
   - Example: "80-country operations → security complexity grows exponentially"
   - Example: "AWS infrastructure choice → forward-thinking tech strategy"

3. **ICP Alignment**: Ties seller's value prop to buyer's exact growth stage
   - Example: Series B + rapid hiring → security training need
   - Example: Global expansion + compliance → risk mitigation

4. **No Generic Templates**: Every email is generated fresh with company-specific data
   - Banned: "Hope this finds you well", "I wanted to reach out"
   - Required: ≥2 specific signal citations with numbers/names

---

## API Response Example

### Full Pipeline Output

```json
{
  "success": true,
  "signals": {
    "funding_rounds": "October 20, 2025. Deel announced a $300 million Series E funding round, valuing the company at $17.3 billion.",
    "leadership_changes": "Carlos Santovena joined as Vice President of Operations earlier this year. Carlos leads global operations...",
    "hiring_trends": [
      "Explore career opportunities at Deel and be part of a global team in over 80 countries.",
      "Open position and apply to join Deel."
    ],
    "tech_stack_changes": "Eli Eyal, Director of Infrastructure at Deel, provides insight on why Deel chose to build on AWS.",
    "news_mentions": [
      "Deel Pricing Plans And Costs 2026: Everything You Need To Know — Deel is a popular global workforce management platform..."
    ],
    "raw_signal_count": 25
  },
  "account_brief": "Deel recently announced a $300 million Series E funding round and hired Carlos Santovena as Vice President of Operations. They're actively hiring and have a global presence in over 80 countries.\n\nThis growth creates a need for robust cybersecurity, aligning with the seller's ICP, as Deel's increased scale and remote work model introduce new security risks.",
  "email_subject": "Deel's $300M Series E + 80-Country Expansion",
  "email_body": "Deel's $300 million Series E at a $17.3 billion valuation signals aggressive expansion. With Carlos Santovena now leading operations across 80 countries, your infrastructure complexity just multiplied.\n\nYour AWS build (per Eli Eyal's comments) shows forward-thinking tech strategy. But global remote operations create security blind spots most Series E companies miss until it's too late.\n\nWe've helped 12 Series B-E companies secure distributed teams during hypergrowth. Average result: 67% reduction in security incidents within 90 days.\n\nWould a 15-minute call this week to discuss Deel's specific security posture make sense?\n\nBhoomi",
  "send_status": true,
  "send_message": "Sent via Gmail SMTP to mahajanbhoomi14@gmail.com",
  "execution_log": [
    "🔍 Step 1: tool_signal_harvester — Fetching live buyer signals...",
    "✅ Signals captured: 25 signals found.",
    "   → Funding: Found",
    "   → Hiring: 2 signals",
    "   → News: 1 mentions",
    "🧠 Step 2: tool_research_analyst — Generating Account Brief...",
    "✅ Account Brief generated.",
    "📧 Step 3: tool_outreach_automated_sender — Drafting and dispatching email...",
    "✅ Sent via Gmail SMTP to mahajanbhoomi14@gmail.com"
  ],
  "error": null
}
```

---

## Error Handling

| Error Scenario | Orchestrator Behavior |
|----------------|----------------------|
| No signals found | Halt pipeline, return `{"success": false, "error": "No signals found for {company}"}` |
| API rate limit | Return error with retry suggestion |
| Email send failure | Return `{"sent": false, "send_message": "SMTP error: ..."}` |
| Invalid ICP/company | Return 400 with validation error |

---

## Performance Metrics

- **Average Pipeline Time**: 8-12 seconds
- **Signal Harvest**: 2-3 seconds (SerpAPI + NewsAPI)
- **Account Brief Generation**: 2-3 seconds (Groq LLM)
- **Email Generation + Send**: 3-4 seconds (Groq LLM + Gmail SMTP)

---

## Tech Stack Rationale

| Choice | Reason |
|--------|--------|
| **Groq Llama 3.3 70B** | Fastest inference (300+ tokens/sec), high quality, free tier |
| **FastAPI** | Async support, auto-generated docs, production-ready |
| **Next.js 14** | App Router, server components, Vercel deployment |
| **SerpAPI** | Real Google results, 100 free searches/month |
| **NewsAPI** | Recent news mentions, free tier |
| **Gmail SMTP** | Zero setup, direct inbox delivery, no API limits |

---

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│  Vercel (Frontend)                          │
│  - Next.js 14 App Router                    │
│  - Static + Server Components               │
│  - Env: NEXT_PUBLIC_API_URL                 │
└──────────────┬──────────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────────┐
│  Render (Backend)                           │
│  - FastAPI + Uvicorn                        │
│  - Python 3.11                              │
│  - Env: GROQ_API_KEY, SERP_API_KEY, etc.    │
└──────────────┬──────────────────────────────┘
               │
               ├─→ Groq API (LLM)
               ├─→ SerpAPI (Signals)
               ├─→ NewsAPI (News)
               └─→ Gmail SMTP (Email)
```

---

## Future Enhancements

1. **Multi-signal scoring**: Rank signals by relevance to ICP
2. **A/B testing**: Generate 2-3 email variants, track open rates
3. **Follow-up sequences**: Auto-send follow-ups based on engagement
4. **CRM integration**: Sync sent emails to Salesforce/HubSpot
5. **Webhook support**: Notify on email open/click events

---

## License

MIT License - Built for Rabbitt AI submission by Bhoomi Mahajan
