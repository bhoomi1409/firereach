# 🚀 Deploy FireReach v3 (Autonomous Version)

## Current Issue
The deployed version is still using the old API:
- **Old:** `{"icp": "...", "target_company": "...", "recipient_email": "...", "sender_name": "..."}`
- **New:** `{"what_we_do": "...", "what_they_do": "...", "why_they_need_us": "...", "max_companies": 5}`

## Quick Fix - Update Render

### Step 1: Update Start Command
In Render dashboard, change the start command to:
```bash
uvicorn main_v3:app --host 0.0.0.0 --port $PORT
```

### Step 2: Add Missing Dependencies
Make sure `requirements.txt` includes:
```
python-pptx==0.6.21
```

### Step 3: Environment Variables
Ensure these are set in Render:
```bash
HUNTER_API_KEY=your_hunter_key
GROQ_API_KEY=your_groq_key
SERPER_API_KEY=your_serper_key
NEWS_API_KEY=your_news_key
SMTP_USER=your_gmail
SMTP_APP_PASSWORD=your_app_password
ICP_THRESHOLD=55
```

## Alternative: Replace main.py

If you can't change the start command, replace the content of `main.py` with `main_v3.py`:

```bash
# In your repo
cp backend/main_v3.py backend/main.py
git add .
git commit -m "Deploy autonomous v3 API"
git push
```

## Test New Deployment

Once deployed, test with:
```bash
curl -X POST https://firereach-cgko.onrender.com/api/outreach \
  -H "Content-Type: application/json" \
  -d '{
    "what_we_do": "We sell AI automation",
    "what_they_do": "SaaS companies", 
    "why_they_need_us": "need better outreach",
    "max_companies": 2
  }'
```

Should return:
```json
{
  "batch_id": "...",
  "icp_summary": "SaaS companies",
  "companies_discovered": 0,
  "companies_scored": 0,
  "companies_passed_icp": 0,
  "companies_contacted": 0,
  "results": [],
  "skipped": [...]
}
```

## Frontend Update

The frontend also needs to be updated to use the new 3-parameter form. Make sure `firereach/frontend/components/ICPForm.tsx` is using the autonomous version.