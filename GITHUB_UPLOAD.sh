#!/bin/bash

echo "🚀 FireReach - GitHub Upload Script"
echo "===================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Node
node_modules/
npm-debug.log*
.next/
out/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
EOF
    echo "✅ .gitignore created"
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Commit
echo "💾 Creating commit..."
git commit -m "FireReach - Autonomous Outreach Engine for Rabbitt AI

- 3-tool sequential agentic pipeline
- Deterministic signal harvesting (SerpAPI + NewsAPI)
- AI-powered research & email generation (Groq Llama 3.3 70B)
- Autonomous email delivery (Gmail SMTP)
- Premium Mission Control UI (Next.js 14 + Tailwind)
- Production-ready with comprehensive error handling
- Deployment configs for Render + Vercel"

echo "✅ Commit created"

# Check if remote exists
if git remote | grep -q "origin"; then
    echo "⚠️  Remote 'origin' already exists"
    echo "Current remote URL:"
    git remote get-url origin
    echo ""
    read -p "Do you want to push to this remote? (y/n): " push_confirm
    if [ "$push_confirm" = "y" ]; then
        echo "🚀 Pushing to GitHub..."
        git push -u origin main || git push -u origin master
        echo "✅ Pushed to GitHub!"
    fi
else
    echo ""
    echo "📝 Next steps:"
    echo "1. Create a new repository on GitHub: https://github.com/new"
    echo "2. Name it: firereach"
    echo "3. Make it public"
    echo "4. DO NOT initialize with README"
    echo ""
    echo "Then run these commands:"
    echo ""
    echo "git remote add origin https://github.com/YOUR-USERNAME/firereach.git"
    echo "git branch -M main"
    echo "git push -u origin main"
    echo ""
fi

echo ""
echo "🎉 Git setup complete!"
echo ""
echo "📋 Repository Info:"
echo "- Branch: $(git branch --show-current)"
echo "- Commits: $(git rev-list --count HEAD)"
echo "- Files tracked: $(git ls-files | wc -l)"
echo ""
echo "🔗 After pushing to GitHub:"
echo "1. Deploy backend to Render"
echo "2. Deploy frontend to Vercel"
echo "3. Test live URLs"
echo ""
