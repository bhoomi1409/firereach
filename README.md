<div align="center">

# 🔥 FireReach

### Autonomous Outreach Engine

*Signal → Research → Send. Zero humans. Zero templates.*

![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi) ![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js) ![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)

[Live Demo](https://your-vercel-url.vercel.app) · [API Docs](https://your-render-url.onrender.com/docs) · [Submission](https://docs.google.com/forms/...)

</div>

---

## What is FireReach?

FireReach is a fully autonomous outreach engine built for GTM and SDR teams. You provide an ICP and a target company. FireReach does the rest:

1. **Harvests live buyer signals** — funding rounds, hiring trends, leadership changes, tech stack shifts
2. **Synthesizes an Account Brief** — 2-paragraph research grounded in real data
3. **Writes + sends a personalized email** — automatically, no human approval

Built for the **Rabbitt AI — Agentic AI Developer** role submission.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **LLM** | Groq API — Llama 3.3 70B | Fastest inference, function calling support |
| **Backend** | FastAPI (Python 3.11) | Async, auto docs at /docs, production-ready |
| **Frontend** | Next.js 14 + TypeScript | App Router, type-safe, Vercel-ready |
| **Signal Source 1** | SerpAPI | Real Google search results — deterministic |
| **Signal Source 2** | NewsAPI | Recent news mentions for target company |
| **Email Delivery** | Gmail SMTP | Zero setup, direct inbox delivery |
| **Styling** | Tailwind CSS | Utility-first, dark theme |
| **Deployment** | Render + Vercel | Free tier, instant deploy |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Next.js UI)                    │
│          ICP + Target Company + Recipient Email         │
└──────────────────────┬──────────────────────────────────┘
                       │ POST /api/outreach
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │            Agent Orchestrator                   │  │
│  │                                                 │  │
│  │  STEP 1: tool_signal_harvester                 │  │
│  │    ├── SerpAPI → funding, hiring, leadership   │  │
│  │    ├── SerpAPI → tech stack changes            │  │
│  │    └── NewsAPI → recent news mentions          │  │
│  │    ↓ SignalData (deterministic)                │  │
│  │                                                 │  │
│  │  STEP 2: tool_research_analyst                 │  │
│  │    ├── Input: SignalData + ICP                 │  │
│  │    ├── Groq Llama 3.3 70B                      │  │
│  │    └── Output: 2-paragraph Account Brief       │  │
│  │    ↓ Account Brief                             │  │
│  │                                                 │  │
│  │  STEP 3: tool_outreach_automated_sender        │  │
│  │    ├── Input: Brief + Signals + ICP            │  │
│  │    ├── Groq Llama 3.3 70B → email generation   │  │
│  │    └── Gmail SMTP → auto-dispatch              │  │
│  │    ↓ {subject, body, sent: true}               │  │
│  │                                                 │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ OutreachResponse
                       ▼
┌─────────────────────────────────────────────────────────┐
│           Results Dashboard (Next.js)                   │
│    Agent Log · Signal Cards · Account Brief · Email    │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/outreach` | Run full agent pipeline |
| `GET` | `/docs` | Auto-generated Swagger UI |

### POST `/api/outreach`

**Request:**
```json
{
  "icp": "We sell high-end cybersecurity training to Series B startups",
  "target_company": "Deel",
  "recipient_email": "prospect@company.com",
  "sender_name": "Alex"
}
```

**Response:**
```json
{
  "success": true,
  "signals": {
    "funding_rounds": "Deel raised $300M Series E...",
    "hiring_trends": ["Deel hiring 50+ engineers...", "..."],
    "leadership_changes": "Joe Kauffman appointed CFO...",
    "tech_stack_changes": "Deel migrating to AWS...",
    "news_mentions": ["Deel expands to 150 countries..."],
    "raw_signal_count": 8
  },
  "account_brief": "Deel's $300M raise and aggressive global expansion...",
  "email_subject": "Deel's $300M raise + 50 new hires = security gap?",
  "email_body": "Noticed Deel just closed $300M Series E...",
  "send_status": true,
  "send_message": "Sent via Gmail SMTP to prospect@company.com",
  "execution_log": [
    "🔍 Step 1: tool_signal_harvester — Fetching live signals...",
    "✅ Signals captured: 8 signals found.",
    "🧠 Step 2: tool_research_analyst — Generating Account Brief...",
    "✅ Account Brief generated.",
    "📧 Step 3: tool_outreach_automated_sender — Dispatching...",
    "✅ Sent via Gmail SMTP to prospect@company.com"
  ]
}
```

---

## Project Structure

```
firereach/
├── backend/
│   ├── main.py                    # FastAPI app + CORS + routes
│   ├── requirements.txt
│   ├── agent/
│   │   ├── orchestrator.py        # 3-step sequential pipeline
│   │   ├── prompts.py             # System prompt + tool prompts
│   │   └── tools/
│   │       ├── signal_harvester.py   # Deterministic — SerpAPI + NewsAPI
│   │       ├── research_analyst.py   # AI — Groq LLM
│   │       └── outreach_sender.py    # AI + Gmail SMTP
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── services/
│       ├── serp_service.py        # SerpAPI wrapper
│       ├── llm_service.py         # Groq client wrapper
│       └── email_service.py       # Gmail SMTP sender
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Input form
│   │   └── result/page.tsx        # Results dashboard
│   ├── components/                # UI components
│   └── lib/api.ts                 # API client
├── DOCS.md                        # Technical documentation
└── README.md                      # This file
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- API Keys: Groq, SerpAPI, NewsAPI, Gmail App Password

### Backend
```bash
cd backend
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Fill in your API keys

uvicorn main:app --reload
# Running at http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
# Running at http://localhost:3000
```

---

## Environment Variables

### Backend `.env`
```bash
GROQ_API_KEY=gsk_...          # groq.com — free
SERP_API_KEY=...               # serpapi.com — 100 searches/month free
NEWS_API_KEY=...               # newsapi.org — free
SMTP_USER=your@gmail.com       # your Gmail
SMTP_APP_PASSWORD=xxxx xxxx    # Google Account → Security → App Passwords
```

### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## Deployment

### Backend → Render
- Root: `backend/`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add all env vars in Render dashboard

### Frontend → Vercel
- Root: `frontend/`
- Framework: Next.js
- Env: `NEXT_PUBLIC_API_URL=https://your-app.onrender.com`

---

## The Rabbitt Challenge

```
ICP:    "We sell high-end cybersecurity training to Series B startups"
Target: "Deel"
Task:   Find growth signals → send personalized email connecting
        their expansion to our security training
```

FireReach handles this end-to-end in ~10 seconds.

---

<div align="center">

Built by **Bhoomi Mahajan** for **Rabbitt AI — Agentic AI Developer Role**

</div>
