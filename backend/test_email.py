#!/usr/bin/env python3
"""
Test email sending directly
"""
import os
from email_sender_v4 import send_with_brochure

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# Test email sending
log = []
result = send_with_brochure(
    to_email="mahajanbhoomi14@gmail.com",  # Send to self for testing
    subject="FireReach v4 Test Email",
    body="Hi there,\n\nThis is a test email from FireReach v4.\n\nBest regards,\nFireReach Team",
    brochure_html="<div style='font-family:Arial;padding:20px;border:1px solid #ccc'><h1>Test Brochure</h1><p>This is a test HTML brochure.</p></div>",
    company_name="Test Company",
    log=log
)

print(f"Email sent: {result}")
print("Log:")
for entry in log:
    print(f"  {entry}")