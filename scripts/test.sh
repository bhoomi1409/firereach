#!/bin/bash

echo "🧪 FireReach Test Script"
echo "======================="

# Test backend health
echo "Testing backend health..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$response" = "200" ]; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed (HTTP $response)"
    echo "Make sure backend is running: cd backend && uvicorn main:app --reload"
    exit 1
fi

# Test full pipeline with Rabbitt Challenge data
echo ""
echo "Testing full pipeline with Rabbitt Challenge data..."

curl -X POST http://localhost:8000/api/outreach \
  -H "Content-Type: application/json" \
  -d '{
    "icp": "We sell high-end cybersecurity training to Series B startups.",
    "target_company": "Deel",
    "recipient_email": "test@example.com",
    "sender_name": "Alex"
  }' \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo ""
echo "🎉 Test complete!"
echo ""
echo "Expected results:"
echo "- success: true"
echo "- signals.raw_signal_count > 0"
echo "- account_brief contains specific signals"
echo "- email_subject contains company name + signal"
echo "- email_body cites specific signals"