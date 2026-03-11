# 🚀 Deployment Guide - Render + Vercel

## Part 1: Deploy Backend to Render (5 minutes)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your GitHub repos

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub account if not already connected
3. Select repository: `bhoomi1409/firereach`
4. Click "Connect"

### Step 3: Configure Service
Fill in these settings:

```
Name: firereach-backend
Region: Oregon (US West) or closest to you
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

### Step 4: Add Environment Variables
Click "Advanced" → "Add Environment Variable" and add these:

```
GROQ_API_KEY=your_groq_key_here
SERP_API_KEY=your_serpapi_key_here
NEWS_API_KEY=your_newsapi_key_here
SMTP_USER=your_email@gmail.com
SMTP_APP_PASSWORD=your_app_password_here
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 3-5 minutes for deployment
3. Once deployed, you'll see: "Your service is live 🎉"
4. Copy your backend URL (looks like: `https://firereach-backend.onrender.com`)

### Step 6: Test Backend
```bash
curl https://your-backend-url.onrender.com/health
```

Should return: `{"status":"ok","service":"FireReach"}`

---

## Part 2: Deploy Frontend to Vercel (3 minutes)

### Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub
3. Authorize Vercel to access your GitHub repos

### Step 2: Import Project
1. Click "Add New..." → "Project"
2. Import `bhoomi1409/firereach`
3. Click "Import"

### Step 3: Configure Project
Fill in these settings:

```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build (auto-detected)
Output Directory: .next (auto-detected)
Install Command: npm install (auto-detected)
```

### Step 4: Add Environment Variable
Click "Environment Variables" and add:

```
Key: NEXT_PUBLIC_API_URL
Value: https://your-backend-url.onrender.com
```

**IMPORTANT**: Replace `your-backend-url` with your actual Render URL from Part 1!

### Step 5: Deploy
1. Click "Deploy"
2. Wait 2-3 minutes for build
3. Once deployed, you'll see: "Congratulations! 🎉"
4. Copy your frontend URL (looks like: `https://firereach-xyz.vercel.app`)

### Step 6: Test Frontend
1. Open your Vercel URL in browser
2. You should see the FireReach Mission Control interface
3. Fill in the form:
   - ICP: "We sell high-end cybersecurity training to Series B startups."
   - Target: "Deel"
   - Email: mahajanbhoomi14@gmail.com
   - Name: Bhoomi
4. Click "Launch Agent 🚀"
5. Check your Gmail for the email!

---

## Part 3: Update Documentation

### Update README.md
Replace placeholder URLs with your actual URLs:

```markdown
[Live Demo](https://firereach-xyz.vercel.app)
[API Docs](https://firereach-backend.onrender.com/docs)
```

### Commit and Push
```bash
cd firereach
git add README.md
git commit -m "Update README with live deployment URLs"
git push origin main
```

---

## Troubleshooting

### Backend Issues

**Problem**: Build fails with "Module not found"
**Solution**: Check that `Root Directory` is set to `backend`

**Problem**: Service crashes on startup
**Solution**: Check logs in Render dashboard, verify all env vars are set

**Problem**: CORS errors
**Solution**: Backend already has CORS configured for all origins (`allow_origins=["*"]`)

### Frontend Issues

**Problem**: Build fails with "Cannot find module"
**Solution**: Check that `Root Directory` is set to `frontend`

**Problem**: API calls fail with 404
**Solution**: Verify `NEXT_PUBLIC_API_URL` is set correctly (no trailing slash)

**Problem**: Environment variable not working
**Solution**: Redeploy after adding env vars (Vercel requires redeploy)

---

## Quick Reference

### Render Dashboard
- Logs: https://dashboard.render.com → Your Service → Logs
- Env Vars: https://dashboard.render.com → Your Service → Environment
- Redeploy: https://dashboard.render.com → Your Service → Manual Deploy

### Vercel Dashboard
- Deployments: https://vercel.com/dashboard → Your Project → Deployments
- Env Vars: https://vercel.com/dashboard → Your Project → Settings → Environment Variables
- Redeploy: https://vercel.com/dashboard → Your Project → Deployments → Redeploy

---

## Expected URLs

After deployment, you'll have:

- **Backend API**: `https://firereach-backend.onrender.com`
- **API Docs**: `https://firereach-backend.onrender.com/docs`
- **Frontend**: `https://firereach-xyz.vercel.app`

---

## Next Steps

1. ✅ Test the full pipeline with live URLs
2. ✅ Update README.md with actual URLs
3. ✅ Take screenshots for submission
4. ✅ Submit to Rabbitt AI

**Total Time**: ~10 minutes
**Cost**: $0 (both use free tiers)

Good luck! 🚀
