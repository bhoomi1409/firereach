#!/bin/bash

echo "🚀 FireReach Deployment Script"
echo "=============================="

echo "This script will guide you through deploying FireReach to production."
echo ""

# Check if git repo exists
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial FireReach implementation"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository found"
fi

echo ""
echo "Deployment Options:"
echo "1. Render (Backend) + Vercel (Frontend) [Recommended]"
echo "2. Docker Compose (Self-hosted)"
echo "3. Manual deployment instructions"
echo ""

read -p "Choose deployment option (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🔧 Render + Vercel Deployment"
        echo "============================="
        echo ""
        echo "Backend (Render):"
        echo "1. Push code to GitHub"
        echo "2. Connect GitHub repo to Render"
        echo "3. Set root directory: firereach/backend"
        echo "4. Build command: pip install -r requirements.txt"
        echo "5. Start command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
        echo "6. Add environment variables:"
        echo "   - GROQ_API_KEY"
        echo "   - SERP_API_KEY"
        echo "   - NEWS_API_KEY"
        echo "   - RESEND_API_KEY"
        echo "   - SENDER_EMAIL"
        echo ""
        echo "Frontend (Vercel):"
        echo "1. Connect GitHub repo to Vercel"
        echo "2. Set root directory: firereach/frontend"
        echo "3. Framework preset: Next.js"
        echo "4. Add environment variable:"
        echo "   - NEXT_PUBLIC_API_URL=https://your-app.onrender.com"
        echo ""
        echo "📋 render.yaml and vercel.json configs are already included!"
        ;;
    2)
        echo ""
        echo "🐳 Docker Compose Deployment"
        echo "============================"
        echo ""
        echo "1. Create .env file in project root with all API keys"
        echo "2. Run: docker-compose up -d"
        echo "3. Access at http://localhost:3000"
        echo ""
        echo "📋 docker-compose.yml is already configured!"
        ;;
    3)
        echo ""
        echo "📖 Manual Deployment Instructions"
        echo "================================="
        echo ""
        echo "Backend:"
        echo "- Deploy to any Python hosting service"
        echo "- Install requirements.txt"
        echo "- Set environment variables"
        echo "- Run: uvicorn main:app --host 0.0.0.0 --port 8000"
        echo ""
        echo "Frontend:"
        echo "- Deploy to any Node.js hosting service"
        echo "- Run: npm install && npm run build"
        echo "- Set NEXT_PUBLIC_API_URL environment variable"
        echo "- Serve the built application"
        ;;
    *)
        echo "Invalid option selected"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment guide complete!"
echo ""
echo "Don't forget to:"
echo "- Test with the Rabbitt Challenge inputs"
echo "- Monitor API usage (SerpAPI has rate limits)"
echo "- Set up proper error monitoring"