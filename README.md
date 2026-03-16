# 🚀 FireReach v4 - Autonomous B2B Outreach Engine

**Professional AI-powered outreach automation for Series B+ companies**

FireReach v4 is a complete autonomous outreach system that transforms a single ICP description into personalized, executive-level email campaigns with professional brochures.

## 🎯 What FireReach Does

```
Single ICP Text → Discover Companies → Approve Selection → 7 Signals → Professional Email + Brochure → Send
```

**Input**: "We provide AI automation tools for Series B SaaS companies that need to scale customer operations"

**Output**: 
- Discovers 5-20 real companies matching your ICP
- Scores each company against your criteria (12+ threshold)
- Extracts 7 types of business signals per company
- Generates executive-level emails with personalized brochures
- Sends via Gmail SMTP with 90-day deduplication

## ✨ Key Features

### 🧠 **Intelligent Company Discovery**
- **Real Company Data**: Discovers actual Series B+ companies using Serper API
- **Smart Fallback**: Realistic demo companies when API unavailable
- **Industry Matching**: SaaS, Fintech, AI/ML company databases
- **Funding Stage Filtering**: Series A/B/C companies with growth signals

### 📊 **Advanced ICP Scoring**
- **3-Dimensional Scoring**: Company fit (40%) + Pain match (40%) + Structural (20%)
- **Score Range**: 0-100 points with intelligent capping and normalization
- **Keyword Matching**: Industry, funding stage, business challenges
- **Threshold Filtering**: Configurable scoring threshold (default: 12%)
- **Negative Signal Detection**: Automatically excludes companies with layoffs/bankruptcy

### 🎯 **7-Signal Intelligence Engine**
1. **Funding Signals**: Recent raises, Series progression
2. **Hiring Signals**: Executive recruitment, team expansion
3. **Product Signals**: New launches, feature releases
4. **Tech Stack Signals**: Technology gaps, modernization needs
5. **News Signals**: Press coverage, announcements
6. **Social Signals**: LinkedIn activity, thought leadership
7. **Executive Signals**: Leadership changes, promotions

### 📧 **Professional Email Generation**
- **Executive-Level Content**: Fortune 500 appropriate language and tone
- **Signal Integration**: References specific business triggers strategically
- **Formal Brochure Attachments**: Executive business proposals with Times New Roman typography, confidential formatting, and structured sections
- **CAN-SPAM Compliant**: Unsubscribe headers, professional signatures

### 🔒 **Enterprise-Grade Features**
- **90-Day Deduplication**: SQLite-based contact blocking
- **Session Management**: 30-minute TTL, resume capability
- **Rate Limiting**: Configurable send limits (1-20 emails)
- **Error Handling**: Graceful fallbacks, comprehensive logging

## 🏗️ Architecture

### Backend (Python + FastAPI)
```
firereach/backend/
├── main.py                 # FastAPI v4.0 application
├── models/v4_models.py     # Pydantic schemas
├── icp_parser.py          # Groq LLM ICP extraction
├── company_discovery_v4.py # Serper API company search
├── icp_scorer_v4.py       # 3-dimensional scoring
├── signal_engine_v4.py    # 7-signal extraction
├── contact_finder_v4.py   # Hunter.io contact enrichment
├── content_generator_v4.py # Professional email generation
├── email_sender_v4.py     # Gmail SMTP delivery
├── session_store.py       # In-memory session management
└── dedup_store.py         # SQLite deduplication
```

### Frontend (Next.js 14 + TypeScript)
```
firereach/frontend/
├── app/page.tsx           # Single ICP input form
├── app/companies/page.tsx # Company selection with checkboxes
├── app/result/page.tsx    # Results dashboard with brochure preview
└── components/            # Reusable UI components
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Gmail account with App Password
- Groq API key (free tier available)
- Serper API key (optional, has fallback)

### 1. Clone Repository
```bash
git clone https://github.com/bhoomi1409/firereach.git
cd firereach
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# Start backend
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start frontend
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ⚙️ Configuration

### Required Environment Variables

#### Backend (.env)
```bash
# AI/LLM Services
GROQ_API_KEY=gsk_your_groq_api_key_here

# Company Discovery (optional - has fallback)
SERP_API_KEY=your_serper_api_key_here

# Contact Enrichment
HUNTER_API_KEY=your_hunter_api_key_here

# Email Delivery
SMTP_USER=your-email@gmail.com
SMTP_APP_PASSWORD=your_gmail_app_password

# Optional Services
NEWS_API_KEY=your_news_api_key_here
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Key Setup

#### 1. Groq API (Required)
- Visit: https://console.groq.com
- Create account and generate API key
- Free tier: 30 requests/minute

#### 2. Gmail SMTP (Required)
- Enable 2FA on Gmail account
- Generate App Password: Google Account → Security → App Passwords
- Use app password (not regular password)

#### 3. Serper API (Optional)
- Visit: https://serper.dev
- Free tier: 2,500 searches/month
- Fallback: Uses realistic demo companies

#### 4. Hunter.io (Optional)
- Visit: https://hunter.io
- Free tier: 25 searches/month
- Fallback: Generates demo contacts

## 📖 Usage Guide

### 1. Single ICP Input
Enter your Ideal Customer Profile in natural language:

```
"We provide AI automation tools for Series B SaaS companies 
that need to scale their customer operations and reduce 
manual workflows by 60%"
```

### 2. Company Discovery
System automatically:
- Parses ICP using Groq LLM
- Discovers 5-20 matching companies
- Shows company list with approval checkboxes

### 3. Company Selection
- Review discovered companies
- Check/uncheck companies to target
- Add manual companies if needed
- Click "Run Outreach"

### 4. Results Dashboard
View complete results:
- Email delivery status
- ICP scores and signals used
- Professional email content
- HTML brochure previews
- Detailed execution logs

## 🔧 API Reference

### Core Endpoints

#### POST /api/discover
Discover companies from ICP text
```json
{
  "icp_text": "We build AI voice agents for fintech companies",
  "target_count": 5
}
```

#### PATCH /api/session/{session_id}/companies
Update company selection
```json
{
  "approved_names": ["Notion", "Linear", "Retool"]
}
```

#### POST /api/run
Execute outreach pipeline
```json
{
  "session_id": "abc123",
  "max_send": 5
}
```

#### GET /api/status/{session_id}
Get session status
```json
{
  "status": "running|completed|failed",
  "batch_id": "xyz789",
  "result": {...}
}
```

#### GET /api/run/stream/{session_id}
Real-time progress via Server-Sent Events
```
data: {"step": "processing_company_1", "progress": 20, "message": "Processing Notion (1/5)"}
data: {"step": "processing_company_2", "progress": 40, "message": "Processing Linear (2/5)"}
data: {"step": "completed", "progress": 100, "message": "All companies processed"}
```

### Follow-up Endpoints

#### GET /api/followups/{batch_id}
Get follow-up drafts for completed batch
```json
{
  "followups": [
    {
      "company_name": "Notion",
      "trigger_signal": {...},
      "draft_subject": "Follow-up: Funding update at Notion",
      "draft_body": "Hi Sarah, I wanted to follow up...",
      "scheduled_at": "2026-03-23T10:00:00Z",
      "status": "pending"
    }
  ],
  "batch_id": "xyz789"
}
```

#### POST /api/followups/{draft_id}/approve
Approve and send follow-up draft
```json
{
  "status": "approved",
  "draft_id": "draft123",
  "sent": true
}
```

### Response Schemas

#### Company Discovery Response
```json
{
  "session_id": "abc123",
  "icp_parsed": {
    "what_we_do": "AI automation tools",
    "target_industry": "saas",
    "target_stage": "series_b",
    "buyer_titles": ["CTO", "VP Engineering"],
    "threshold": 12
  },
  "companies": [
    {
      "name": "Notion",
      "domain": "notion.so",
      "reason": "productivity workspace - Series C funded",
      "approved": true
    }
  ]
}
```

#### Outreach Results Response
```json
{
  "batch_id": "xyz789",
  "companies_discovered": 5,
  "companies_passed_icp": 3,
  "emails_sent": 2,
  "results": [
    {
      "company_name": "Notion",
      "icp_score": 44.0,
      "signals_used": [
        {
          "type": "funding",
          "summary": "Notion raised $275M Series C",
          "final_score": 0.92
        }
      ],
      "contact": {
        "email": "sarah.chen@notion.so",
        "first_name": "Sarah",
        "title": "VP Engineering"
      },
      "email_subject": "AI Automation for Notion",
      "sent": true
    }
  ]
}
```

## 🎨 Customization

### Email Templates
Modify `content_generator_v4.py` for email content and formal brochure templates:
```python
_SYSTEM = """You are a senior executive writing high-level B2B emails..."""

# Formal brochure template uses Times New Roman typography with:
# - Executive letterhead styling
# - Confidential business proposal formatting  
# - Structured sections with professional spacing
# - Corporate color scheme and typography
```

### ICP Scoring
Adjust weights in `icp_scorer_v4.py`:
```python
fit_pts = round(fit * 40, 1)      # Company fit: 40%
pain_pts = round(pain * 40, 1)    # Pain match: 40%
struct = 20                       # Structural: 20%
total = round(min(100, fit_pts + pain_pts + struct), 1)  # Capped at 100
```

### Signal Types
Configure signal weights in `signal_engine_v4.py`:
```python
SIGNAL_WEIGHTS = {
    "funding": 1.0,    # Highest priority
    "hiring": 0.95,
    "product": 0.75,
    # ... customize weights
}
```

## 🚀 Deployment

### Production Environment Variables
```bash
# Use production URLs
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# Production email settings
SMTP_USER=noreply@yourdomain.com
SMTP_APP_PASSWORD=production_app_password

# Production API keys
GROQ_API_KEY=production_groq_key
SERP_API_KEY=production_serper_key
```

### Backend Deployment (Render)
1. Connect GitHub repository
2. Set environment variables
3. Deploy command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)
1. Connect GitHub repository
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Auto-deploy on push

### Docker Deployment
```bash
# Backend
cd backend
docker build -t firereach-backend .
docker run -p 8000:8000 --env-file .env firereach-backend

# Frontend
cd frontend
docker build -t firereach-frontend .
docker run -p 3000:3000 firereach-frontend
```

## 🔍 Monitoring & Analytics

### Health Checks
```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "version": "4.0"}
```

### Logging
- Backend logs: Console output with structured logging
- Email delivery: SMTP success/failure tracking
- ICP scoring: Detailed scoring breakdowns
- Signal extraction: Signal type and relevance scores

### Performance Metrics
- Average processing time: 15-30 seconds per company
- Email delivery rate: 95%+ (with valid SMTP)
- ICP scoring accuracy: Configurable threshold
- Deduplication effectiveness: 90-day blocking

## 🛠️ Development

### Running Tests
```bash
# Backend tests
cd backend
python test_full_pipeline.py
python comprehensive_test.py

# Frontend tests
cd frontend
npm run lint
npm run build
```

### Code Structure
- **Models**: Pydantic schemas in `models/v4_models.py`
- **Services**: Modular services for each pipeline step
- **API**: FastAPI with automatic OpenAPI documentation
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS

### Adding New Features
1. **New Signal Type**: Add to `signal_engine_v4.py`
2. **New Data Source**: Extend `company_discovery_v4.py`
3. **New Email Template**: Modify `content_generator_v4.py`
4. **New UI Component**: Add to `frontend/components/`

## 🔒 Security & Compliance

### Data Protection
- **No Data Storage**: Companies and contacts not permanently stored
- **Session TTL**: 30-minute automatic expiration
- **API Rate Limiting**: Configurable request limits
- **Environment Variables**: Sensitive data in .env files

### Email Compliance
- **CAN-SPAM**: Unsubscribe headers on all emails
- **GDPR**: No personal data retention
- **Professional Standards**: Executive-level content only
- **Deduplication**: 90-day contact blocking

### Security Best Practices
- **API Key Rotation**: Regular key updates recommended
- **HTTPS Only**: Production deployment over SSL
- **Input Validation**: Pydantic schema validation
- **Error Handling**: No sensitive data in error messages
- **HTML Sanitization**: All user inputs escaped in brochure templates

## ⚠️ Known Issues & Fixes

### P0 - Critical Race Conditions (FIXED)

#### Double-click "Find Companies" ✅ FIXED
**Issue**: User clicks twice → two POST /api/discover calls run in parallel → two sessions created → duplicate results, wasted API credits
**Fix Applied**: 
- Frontend: Disable button immediately on first click with `if (loading) return`
- Button shows spinner and prevents multiple submissions
- State management prevents race conditions

#### Double-click "Run Outreach" ✅ FIXED  
**Issue**: User clicks Run twice → two POST /api/run calls with same session_id → same companies emailed TWICE within seconds
**Fix Applied**:
- Frontend: Added `if (loading) return` guard to prevent double-clicks
- Backend: Session status locking with 409 Conflict response
- Atomic session status management prevents concurrent runs

#### SQLite Concurrent Writes ✅ FIXED
**Issue**: 3 companies processed in parallel → all try to write to SQLite simultaneously → "database is locked" error
**Fix Applied**:
- Added `check_same_thread=False` to sqlite3.connect()
- Enabled WAL mode: `PRAGMA journal_mode=WAL` for concurrent access
- Prevents database lock errors during parallel processing

#### Groq Rate Limiting ✅ FIXED
**Issue**: Batch of 10 companies → all hit Groq API simultaneously → guaranteed rate limit (30 req/min free tier)
**Fix Applied**:
- Added separate `groq_sem = asyncio.Semaphore(1)` for serial Groq calls
- Added 0.5s delay between Groq API calls
- Prevents rate limit errors while maintaining parallel company processing

#### Exception Handling ✅ FIXED
**Issue**: Uncaught exceptions in company processing → company_name="unknown" in results
**Fix Applied**:
- Wrapped entire process() function in try/except
- Returns CompanyResult with proper company_name on any exception
- Detailed error logging without exposing stack traces

#### Email Retry Logic ✅ FIXED
**Issue**: Gmail SMTP timeout mid-batch → lost emails, incomplete campaigns
**Fix Applied**:
- 3 retries with exponential backoff (2s, 4s, 8s delays)
- Specific handling for SMTPServerDisconnected and SMTPConnectError
- Detailed retry logging for debugging

#### Session Status API ✅ FIXED
**Issue**: User refreshes page mid-pipeline → loses state, no way to check status
**Fix Applied**:
- Added GET /api/status/{session_id} endpoint
- Session status tracking: running, completed, failed
- Prevents concurrent pipeline runs with 409 Conflict

### P1 - Data Validation Issues (FIXED)

#### ICP Threshold Too Low ✅ FIXED
**Issue**: Default threshold=12 means almost EVERY company passes (including irrelevant ones)
**Fix Applied**:
- Changed threshold from 12 to 55 in `models/v4_models.py`
- 55 is proper midpoint for 0-100 scoring system
- Prevents sending to irrelevant companies

#### Empty Contact Email ✅ FIXED
**Issue**: Empty email strings pass truthy check → send attempted anyway
**Fix Applied**:
- Enhanced contact validation: `if not contact or not contact.email or not contact.email.strip()`
- Catches empty strings and whitespace-only emails
- Prevents failed send attempts

#### HTML Injection in Brochure ✅ FIXED
**Issue**: Company name with `<script>` tags injected into HTML brochure
**Fix Applied**:
- Added `import html` and `html.escape()` for all user-controlled strings
- Sanitizes company names, signal summaries, and ICP data
- Prevents XSS attacks in email clients

#### Max Send Validation ✅ FIXED
**Issue**: max_send=0 or negative → no emails but 200 OK response (confusing)
**Fix Applied**:
- Added validation: raises 400 error if max_send <= 0
- Proper clamping: `max_send = min(max(1, req.max_send or 5), 20)`
- Clear error messages for invalid input

#### Brochure HTML Truncation ✅ FIXED
**Issue**: 14KB hard cut can break HTML mid-tag → broken email rendering
**Fix Applied**:
- Smart truncation at last closing tag before 14KB limit
- Finds `</tag>` boundary and preserves HTML structure
- Prevents broken HTML in email attachments

#### Checkbox Race Conditions ✅ FIXED
**Issue**: Rapid checkbox clicks → multiple PATCH calls → wrong final state
**Fix Applied**:
- 300ms debounce on checkbox updates
- Clears previous timeout on new clicks
- Sends complete approved_names list (last write wins)

### P1 - Missing Features (IMPLEMENTED)

#### Session Recovery & Status API ✅ IMPLEMENTED
**Issue**: User refreshes page mid-pipeline → loses state, no way to check status
**Implementation**: 
- Added GET /api/status/{session_id} endpoint
- Session status tracking: running, completed, failed
- Prevents concurrent pipeline runs with 409 Conflict

#### Real-time Progress Updates ✅ IMPLEMENTED
**Issue**: 15-30 second black box creates user anxiety
**Implementation**: 
- Server-Sent Events (SSE) via GET /api/run/stream/{session_id}
- Real-time progress bar with company-by-company updates
- Frontend EventSource integration with progress display

#### Follow-up Engine ✅ IMPLEMENTED
**Issue**: No signal-triggered follow-ups or second touch campaigns
**Implementation**:
- Signal diff detection between outreach runs
- Automated follow-up draft generation
- API endpoints: GET /api/followups/{batch_id}, POST /api/followups/{draft_id}/approve
- Scheduled follow-ups based on new trigger signals

#### Demo Company Detection ✅ IMPLEMENTED
**Issue**: Users confused when Serper API fails, try to email fake contacts
**Implementation**:
- Added `is_demo: bool` field to DiscoveredCompany model
- Frontend banner: "Demo Mode Active - Add Serper API key for real companies"
- Clear distinction between real and demo company data

#### Enhanced Enrichment ✅ IMPLEMENTED
**Issue**: Missing enrichment.py as separate module
**Implementation**:
- Created enrichment_v4.py with Hunter.io and NewsAPI integration
- Parallel data enrichment from multiple sources
- Comprehensive company profiles with emails, news, and metadata

### P2 - UX Improvements (IMPLEMENTED)

#### Demo Company Detection ✅ IMPLEMENTED
**Issue**: Demo companies shown as real when Serper API unavailable
**Implementation**: 
- `is_demo: bool` field marks fallback companies
- Frontend banner warns users about demo mode
- Clear call-to-action to add Serper API key

#### Brochure HTML Truncation ✅ IMPLEMENTED
**Issue**: 14KB hard cut can break HTML mid-tag
**Implementation**: 
- Smart truncation at last closing HTML tag before 14KB limit
- Preserves HTML structure integrity in email attachments
- Prevents broken rendering in email clients

#### Hunter Catch-all Protection ✅ IMPLEMENTED
**Issue**: Domains with catch-all MX accept any email → hard bounces
**Implementation**: 
- Check `accept_all` flag in Hunter.io responses
- Skip catch-all domains in T2 verification
- Prevents reputation damage from invalid addresses

#### Real-time Progress Bar ✅ IMPLEMENTED
**Issue**: Users anxious during 15-30 second processing time
**Implementation**:
- Server-Sent Events stream processing updates
- Visual progress bar with percentage and current company
- Step-by-step pipeline visibility

### Performance Optimizations Applied

#### Rate Limiting Strategy
- **Groq API**: Serial calls with 0.5s delay (prevents 429 errors)
- **Company Processing**: Parallel with Semaphore(3) (optimal throughput)
- **SQLite**: WAL mode for concurrent reads/writes

#### Error Recovery
- **Email Sending**: Graceful fallbacks with detailed logging
- **API Failures**: Fallback to demo data when external APIs fail
- **Exception Handling**: Never crash entire batch on single company error

#### Memory Management
- **Session TTL**: 30-minute automatic cleanup
- **In-Memory Store**: Suitable for demo, Redis recommended for production
- **Batch Size**: Capped at 20 companies maximum

### Monitoring & Debugging

#### Execution Logs
- **Per-Company**: Detailed step-by-step processing logs
- **Error Tracking**: Specific error messages without stack traces
- **Performance**: Processing time and API call tracking

#### Health Checks
- **Backend**: `/health` endpoint with version info
- **Database**: SQLite connection and WAL mode verification
- **APIs**: Graceful degradation when external services fail

### Production Readiness Checklist

✅ **Race Conditions**: All P0 double-click issues fixed
✅ **Database**: SQLite WAL mode for concurrent access  
✅ **Rate Limiting**: Groq API serialization implemented
✅ **Error Handling**: Comprehensive exception catching
✅ **Input Validation**: HTML sanitization and email validation
✅ **Security**: No sensitive data in error responses
✅ **Email Reliability**: 3 retries with exponential backoff
✅ **Session Management**: Status API with running/completed/failed states
✅ **HTML Safety**: Smart brochure truncation at tag boundaries
✅ **UX**: Checkbox debouncing prevents race conditions
✅ **Real-time Updates**: SSE progress streaming implemented
✅ **Follow-ups**: Signal-triggered campaigns with diff detection
✅ **Demo Mode**: Clear distinction between real and demo data
✅ **Enrichment**: Multi-source data enrichment pipeline
✅ **Progress Visibility**: Real-time processing updates
⚠️ **Monitoring**: Basic logging (Redis + structured logging recommended)
⚠️ **Scaling**: In-memory sessions (Redis recommended for production)

## 📊 Performance & Scaling

### Current Limits
- **Companies per batch**: 1-20 (configurable)
- **Processing time**: 15-30 seconds per company
- **API rate limits**: Groq (30/min), Serper (100/day free)
- **Email sending**: Gmail SMTP limits apply

### Scaling Options
- **Redis**: Replace in-memory sessions for multi-instance
- **PostgreSQL**: Replace SQLite for production deduplication
- **Queue System**: Add Celery for background processing
- **Load Balancer**: Multiple backend instances

## 🤝 Contributing

### Development Setup
1. Fork repository
2. Create feature branch
3. Follow code style (Black, ESLint)
4. Add tests for new features
5. Submit pull request

### Code Style
- **Python**: Black formatter, type hints
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional commit messages
- **Documentation**: Update README for new features

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

### Common Issues

#### "No companies discovered"
- Check Serper API key in .env
- Verify ICP text is descriptive (20+ characters)
- System falls back to demo companies if API fails

#### "Email sending failed"
- Verify Gmail App Password (not regular password)
- Check SMTP_USER and SMTP_APP_PASSWORD in .env
- Ensure 2FA enabled on Gmail account

#### "Companies not passing ICP"
- Lower threshold in `models/v4_models.py`
- Check ICP scoring in logs
- Verify company data has sufficient information

### Getting Help
- **Issues**: GitHub Issues for bugs
- **Discussions**: GitHub Discussions for questions
- **Email**: Contact maintainers for enterprise support

## 🎯 Roadmap

### v4.1 (Next Release)
- [ ] Redis session management
- [ ] PostgreSQL deduplication
- [ ] Advanced analytics dashboard
- [ ] Custom email templates UI

### v4.2 (Future)
- [ ] Multi-language support
- [ ] Slack/Teams integrations
- [ ] Advanced signal types
- [ ] A/B testing framework

### v5.0 (Long-term)
- [ ] Multi-tenant architecture
- [ ] Advanced AI personalization
- [ ] CRM integrations
- [ ] Enterprise SSO

---

**FireReach v4** - Built with ❤️ for B2B sales teams who demand professional, intelligent outreach automation.

*Last updated: March 2026*