# 🚀 FireReach - Deploy NOW Guide

## ✅ Pre-Deployment Checklist

- [x] Backend working locally
- [x] Frontend redesigned (premium orange theme)
- [x] All API keys configured
- [x] DOCS.md updated
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Test live URLs

---

## 1. Deploy Backend to Render

### Step 1: Push to GitHub
```bash
cd firereach
git init
git add .
git commit -m "FireReach - Autonomous Outreach Engine"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `firereach-backend`
   - **Root Directory**: `firereach/backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables
In Render dashboard, add these:
```
GROQ_API_KEY=gsk_your_groq_api_key_here
SERP_API_KEY=your_serpapi_key_here
NEWS_API_KEY=your_newsapi_key_here
SMTP_USER=your_email@gmail.com
SMTP_APP_PASSWORD=your_app_password_here
```

### Step 4: Deploy & Get URL
- Click "Create Web Service"
- Wait 3-5 minutes for deployment
- Copy your backend URL: `https://firereach-backend-XXXX.onrender.com`

### Step 5: Test Backend
```bash
curl https://YOUR-BACKEND-URL.onrender.com/health
```

Should return: `{"status":"ok","service":"FireReach"}`

---

## 2. Deploy Frontend to Vercel

### Step 1: Update API URL
Edit `firereach/frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL.onrender.com
```

Commit and push:
```bash
git add .
git commit -m "Update API URL for production"
git push
```

### Step 2: Deploy on Vercel
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `firereach/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Add Environment Variable
In Vercel project settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL.onrender.com
```

### Step 4: Deploy
- Click "Deploy"
- Wait 2-3 minutes
- Get your live URL: `https://firereach-XXXX.vercel.app`

---

## 3. Test Live Deployment

### Test 1: Open Frontend
Visit: `https://YOUR-FRONTEND-URL.vercel.app`

Should see: Premium orange-themed FireReach dashboard

### Test 2: Rabbitt Challenge Test
Fill form with:
```
ICP: "We sell high-end cybersecurity training to Series B startups."
Target Company: "Deel"
Recipient Email: mahajanbhoomi14@gmail.com
Sender Name: Bhoomi
```

Click "Launch Agent 🚀"

### Test 3: Verify Results
- ✅ See 3-step pipeline animation
- ✅ Results page shows signals
- ✅ Account brief displayed
- ✅ Email preview shown
- ✅ Check Gmail inbox for actual email

---

## 4. Submission Package

### Live URLs
```
Frontend: https://YOUR-FRONTEND-URL.vercel.app
Backend: https://YOUR-BACKEND-URL.onrender.com
GitHub: https://github.com/YOUR-USERNAME/firereach
```

### Screenshots to Take
1. Homepage with form filled
2. Loading state with pipeline animation
3. Results page with signals
4. Email in Gmail inbox
5. Backend health check response

### Submission Checklist
- [ ] Both services deployed and live
- [ ] Test completed successfully
- [ ] Email received in inbox
- [ ] Screenshots captured
- [ ] GitHub repo public
- [ ] README.md updated with live URLs

---

## 5. Quick Commands Reference

### Local Development
```bash
# Backend
cd firereach/backend
uvicorn main:app --reload

# Frontend
cd firereach/frontend
npm run dev
```

### Check Logs
```bash
# Render: Dashboard → Logs tab
# Vercel: Dashboard → Deployments → View Function Logs
```

### Redeploy
```bash
git add .
git commit -m "Update"
git push
# Auto-deploys on both Render and Vercel
```

---

## 🎯 Success Criteria

✅ Frontend loads at Vercel URL
✅ Backend health check passes
✅ Form submission works
✅ Pipeline executes all 3 steps
✅ Email arrives in Gmail
✅ Results page displays correctly

---

## 🚨 Troubleshooting

**Backend not starting:**
- Check Render logs
- Verify all environment variables set
- Ensure Python 3.11+ selected

**Frontend can't connect:**
- Verify NEXT_PUBLIC_API_URL is correct
- Check CORS in backend (already configured)
- Redeploy frontend after env var change

**No email received:**
- Check Gmail SMTP credentials
- Verify app password is correct
- Check backend logs for send errors

---

## 📧 Final Test Email

Once deployed, send test email to yourself:
```
ICP: "We sell high-end cybersecurity training to Series B startups."
Target: "Deel"
Email: mahajanbhoomi14@gmail.com
Name: Bhoomi
```

**Expected:** Email arrives within 1 minute with:
- Subject mentioning Deel + specific signal
- Body citing 2+ specific signals
- Professional, peer-level tone

---

**You're ready to deploy! Follow steps 1-3 and you'll have live URLs in 10 minutes.** 🚀
