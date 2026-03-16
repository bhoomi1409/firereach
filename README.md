<div align="center">

# 🔥 FireReach

### Fully Autonomous Outreach Engine

*ICP → Discover → Score → Contact → Send. Zero humans. Zero manual input.*

![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi) ![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js) ![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)

[Live Demo](https://firereach-omega.vercel.app) · [API Docs](https://firereach-cgko.onrender.com/docs) · [GitHub](https://github.com/bhoomi1409/firereach)

</div>

---

## What is FireReach?

FireReach is a **fully autonomous outreach engine** that requires only an ICP description. The system:

1. **Discovers companies** from your ICP using intelligent web search
2. **Enriches & scores** each company against your ideal customer profile  
3. **Finds decision-maker contacts** using Hunter.io's multi-tier fallback system
4. **Harvests live buyer signals** — funding, hiring, news, tech changes
5. **Generates personalized emails + pitch decks** using Groq Llama 3.3 70B
6. **Sends automatically** via Gmail SMTP with PPT attachments and full compliance

**Input:** 3 sentences describing your ICP  
**Output:** Personalized emails + custom PowerPoint presentations sent to qualified prospects

Built for the **Rabbitt AI — Agentic AI Developer** role submission.

---

## New Autonomous Architecture

### Before (Manual)
```json
POST /api/outreach
{
  "icp": "We sell cybersecurity training...",
  "target_company": "Deel",           ← Manual input required
  "recipient_email": "cto@deel.com",  ← Manual research needed
  "sender_name": "Alex"
}
```

### After (Autonomous)
```json
POST /api/outreach
{
  "what_we_do": "We sell AI-powered outreach automation to B2B sales teams",
  "what_they_do": "Series B SaaS companies with a sales team trying to grow pipeline", 
  "why_they_need_us": "Low reply rates, hired new VP Sales, raised funding recently",
  "max_companies": 5
}
```

**Result:** System autonomously discovers 15+ companies, scores them, contacts 5 best matches.

---

## Autonomous Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                           │
│              ICP Description (3 fields)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ POST /api/outreach
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 STEP 0: DISCOVERY                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  • Build smart search queries from ICP          │  │
│  │  • Serper: "Series B SaaS raised funding 2025"  │  │
│  │  • Extract company names from results           │  │
│  │  • Deduplicate & filter (15+ candidates)        │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              STEP 1: ENRICH & SCORE                     │
│  ┌─────────────────────────────────────────────────┐  │
│  │  For each discovered company:                    │  │
│  │  • Serper: domain + description + keywords      │  │
│  │  • Hunter domain-search: verify + get emails    │  │
│  │  • ICP Score: fit + pain + structure (0-100)    │  │
│  │  • Gate: score < 55 → skip, score ≥ 55 → qualify│  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              STEP 2: SIGNALS & CONTACTS                   │
│  ┌─────────────────────────────────────────────────┐  │
│  │  For each qualified company:                     │  │
│  │  • NewsAPI + Serper: recent signals             │  │
│  │  • Hunter T1→T4: find decision-maker email      │  │
│  │  • Groq LLM: generate personalized email        │  │
│  │  • PowerPoint: create custom pitch deck         │  │
│  │  • Gmail SMTP: send with PPT attachment         │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ BatchOutreachResult
                       ▼
┌─────────────────────────────────────────────────────────┐
│              BATCH RESULTS DASHBOARD                    │
│   • 12 companies discovered, 7 passed ICP, 5 contacted │
│   • Per-company: signals, emails, logs, success status │
│   • Skipped list with reasons (low ICP, no contact)    │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **LLM** | Groq API — Llama 3.3 70B | Fastest inference, function calling support |
| **Backend** | FastAPI (Python 3.11) | Async, auto docs at /docs, production-ready |
| **Frontend** | Next.js 14 + TypeScript | App Router, type-safe, Vercel-ready |
| **Discovery** | Serper API | Real Google search results for company discovery |
| **Contact Data** | Hunter.io | T1 domain-search, T2 email-finder, T3 verifier, T4 generic |
| **Signal Sources** | NewsAPI + Serper | Recent news mentions + web signals |
| **Email Delivery** | Gmail SMTP | Zero setup, direct inbox delivery |
| **Styling** | Tailwind CSS | Utility-first, dark theme |
| **Deployment** | Render + Vercel | Free tier, instant deploy |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/outreach` | **NEW:** Autonomous batch outreach |
| `GET` | `/docs` | Auto-generated Swagger UI |

### POST `/api/outreach` (Autonomous)

**Request:**
```json
{
  "what_we_do": "We sell AI-powered outreach automation to B2B sales teams",
  "what_they_do": "Series B SaaS companies with a sales team trying to grow pipeline",
  "why_they_need_us": "Low reply rates, hired new VP Sales, raised funding to grow revenue",
  "max_companies": 5
}
```

**Response:**
```json
{
  "batch_id": "a1b2c3d4",
  "icp_summary": "Series B SaaS companies with a sales team...",
  "companies_discovered": 12,
  "companies_scored": 12,
  "companies_passed_icp": 7,
  "companies_contacted": 5,
  "results": [
    {
      "company_name": "HubSpot",
      "icp_score": 72.5,
      "should_send": true,
      "contact_email": "alex@hubspot.com",
      "contact_name": "Alex Johnson", 
      "contact_title": "VP Engineering",
      "top_signals": ["HubSpot raises $300M Series C", "Hiring 50+ ML Engineers"],
      "email_subject": "HubSpot's ML hiring + $300M — quick question",
      "email_body": "Hi Alex,\n\nSaw HubSpot just raised $300M and you're hiring 50+ ML engineers...",
      "ppt_generated": true,
      "ppt_filename": "HubSpot_20250316_143022.pptx",
      "sent": true,
      "send_message": "Sent via Gmail SMTP with personalized PPT to alex@hubspot.com",
      "log": ["Processing: HubSpot", "[Enrich] domain=hubspot.com", "[Score] 72.5", "..."]
    }
  ],
  "skipped": [
    {"company_name": "Oracle", "skip_reason": "ICP score 18 < threshold 55"},
    {"company_name": "SAP", "skip_reason": "No contact email found"}
  ]
}
```

---

## Project Structure

```
firereach/
├── backend/
│   ├── main_v3.py                    # NEW: Autonomous FastAPI app
│   ├── orchestrator_v3.py            # NEW: Batch pipeline orchestrator  
│   ├── company_discovery.py          # NEW: ICP → company discovery
│   ├── contact_fallback.py           # Hunter.io T1/T2/T3/T4 system
│   ├── fallback_engine.py            # Circuit breaker pattern
│   ├── requirements.txt              # Updated dependencies
│   ├── models/
│   │   └── schemas.py                # Pydantic models
│   └── services/
│       ├── serp_service.py           # Serper API wrapper
│       ├── llm_service.py            # Groq client wrapper
│       └── email_service.py          # Gmail SMTP sender
├── frontend/
│   ├── app/
│   │   ├── page.tsx                  # NEW: Autonomous ICP form
│   │   └── result/page.tsx           # NEW: Batch results dashboard
│   ├── components/
│   │   └── ICPForm.tsx               # NEW: 3-field ICP input
│   └── lib/api.ts                    # Updated API client
├── DOCS.md                           # Technical documentation
└── README.md                         # This file
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- API Keys: Groq, Hunter.io, Serper, NewsAPI, Gmail App Password

### Backend
```bash
cd backend
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Fill in your API keys

uvicorn main_v3:app --reload
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
# Hunter.io — T1 contact enrichment + domain resolution
HUNTER_API_KEY=          # hunter.io → Dashboard → API Keys (25 free/mo)

# LLM
GROQ_API_KEY=            # console.groq.com → API Keys (free)

# Signals + discovery  
NEWS_API_KEY=            # newsapi.org → 100 req/day free
SERPER_API_KEY=          # serper.dev → 2,500/mo free (used for discovery + signals + jobs)

# Email sending (Gmail SMTP — free 500/day)
SMTP_USER=your@gmail.com
SMTP_APP_PASSWORD=xxxx xxxx xxxx xxxx

# ICP scoring threshold (default 55)
ICP_THRESHOLD=55
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
- Start: `uvicorn main_v3:app --host 0.0.0.0 --port $PORT`
- Add all env vars in Render dashboard

### Frontend → Vercel
- Root: `frontend/`
- Framework: Next.js
- Env: `NEXT_PUBLIC_API_URL=https://your-app.onrender.com`

---

## The Autonomous Advantage

### Traditional Outreach Tools
❌ Manual company research  
❌ Manual contact finding  
❌ Template-based emails  
❌ One company at a time  
❌ No ICP scoring  

### FireReach Autonomous
✅ **Discovers companies from ICP description**  
✅ **Finds contacts automatically (Hunter.io T1→T4)**  
✅ **AI-generated personalized emails + pitch decks**  
✅ **Batch processing (5-20 companies)**  
✅ **Semantic ICP scoring & filtering**  
✅ **Live signal harvesting**  
✅ **Full audit trail per company**

---

## Example Autonomous Flow

**Input ICP:**
```
What we do: "We sell AI-powered outreach automation to B2B sales teams"
What they do: "Series B SaaS companies with a sales team trying to grow pipeline"  
Why they need us: "Low reply rates, hired new VP Sales, raised funding recently"
Max companies: 5
```

**System discovers:** HubSpot, Stripe, Notion, Figma, Canva, Deel, Calendly...

**System scores:** HubSpot (72%), Stripe (68%), Notion (45%), Figma (71%)...

**System contacts:** Top 5 companies that passed ICP threshold (≥55%)

**Result:** 5 personalized emails + custom PowerPoint presentations sent to VP Sales/Engineering at qualified companies

---

<div align="center">

Built by **Bhoomi Mahajan** for **Rabbitt AI — Agentic AI Developer Role**

**Fully Autonomous. Zero Manual Work. Maximum Results.**

</div>
