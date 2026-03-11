#!/bin/bash

# 🔥 FireReach - One-Command Setup Script
# Run this after adding your API keys to backend/.env

echo "🔥 FireReach Setup Starting..."
echo "================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check Node version
node_version=$(node --version 2>&1)
echo "✓ Node version: $node_version"

echo ""
echo "📦 Installing Backend Dependencies..."
cd backend
pip install -r requirements.txt
echo "✅ Backend dependencies installed"

echo ""
echo "📦 Installing Frontend Dependencies..."
cd ../frontend
npm install
echo "✅ Frontend dependencies installed"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Add your 4 API keys to backend/.env"
echo "2. Terminal 1: cd backend && uvicorn main:app --reload"
echo "3. Terminal 2: cd frontend && npm run dev"
echo "4. Open http://localhost:3000"
echo ""
echo "🚀 Ready to launch!"