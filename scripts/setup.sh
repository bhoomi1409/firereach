#!/bin/bash

echo "🔥 FireReach Setup Script"
echo "========================="

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 1 ]]; then
    echo "✅ Python $python_version found"
else
    echo "❌ Python 3.11+ required. Current: $python_version"
    exit 1
fi

# Check if Node.js 18+ is installed
node_version=$(node --version 2>&1 | grep -oE '[0-9]+' | head -1)
if [[ $node_version -ge 18 ]]; then
    echo "✅ Node.js v$node_version found"
else
    echo "❌ Node.js 18+ required. Current: v$node_version"
    exit 1
fi

echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API keys"
fi

echo "✅ Backend setup complete"

echo ""
echo "Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

# Copy environment file
if [ ! -f .env.local ]; then
    cp .env.local.example .env.local
    echo "⚠️  Please edit frontend/.env.local with your API URL"
fi

echo "✅ Frontend setup complete"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys:"
echo "   - GROQ_API_KEY (get from https://console.groq.com)"
echo "   - SERP_API_KEY (get from https://serpapi.com)"
echo "   - NEWS_API_KEY (get from https://newsapi.org)"
echo "   - RESEND_API_KEY (get from https://resend.com)"
echo ""
echo "2. Start the backend:"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo ""
echo "3. Start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Visit http://localhost:3000"