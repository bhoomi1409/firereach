#!/bin/bash

echo "🚀 Deploying FireReach v3 - Autonomous Version"

# Navigate to project directory
cd firereach

# Add all changes
git add .

# Commit with deployment message
git commit -m "Deploy FireReach v3: Autonomous API with 3-parameter ICP input

- Replace main.py with autonomous version (main_v3.py)
- Replace orchestrator.py with autonomous version (orchestrator_v3.py)  
- New API: {what_we_do, what_they_do, why_they_need_us, max_companies}
- Old API removed: {icp, target_company, recipient_email, sender_name}
- Batch processing: 1-20 companies automatically
- PowerPoint generation: Personalized presentations attached
- Company discovery: Autonomous from ICP description
- Hunter.io integration: T1-T4 contact finding system"

# Push to GitHub (triggers Render deployment)
git push origin main

echo "✅ Pushed to GitHub"
echo "🔄 Render will auto-deploy in ~2-3 minutes"
echo "🧪 Test with: curl -X POST https://firereach-cgko.onrender.com/api/outreach -H 'Content-Type: application/json' -d '{\"what_we_do\":\"test\",\"what_they_do\":\"test\",\"why_they_need_us\":\"test\"}'"