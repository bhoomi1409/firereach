import resend
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "FireReach <onboarding@resend.dev>")
SMTP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")
SMTP_USER = os.getenv("SMTP_USER")

def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Send email — tries Gmail SMTP first, falls back to Resend.
    Returns {"sent": bool, "message": str}
    """
    
    # Format body with proper HTML for better presentation
    html_body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="white-space: pre-wrap;">{body}</div>
    </body>
    </html>
    """
    
    # --- SMTP (Gmail) - PRIMARY ---
    if SMTP_USER and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart('alternative')
            msg["From"] = SMTP_USER
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Add both plain text and HTML versions
            part1 = MIMEText(body, "plain")
            part2 = MIMEText(html_body, "html")
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, to_email, msg.as_string())
            return {"sent": True, "message": f"Sent via Gmail SMTP to {to_email}"}
        except Exception as e:
            # Try Resend as fallback
            pass
    
    # --- RESEND FALLBACK ---
    if resend.api_key:
        try:
            params = {
                "from": SENDER_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            }
            email = resend.Emails.send(params)
            return {"sent": True, "message": f"Sent via Resend to {to_email}"}
        except Exception as e:
            return {"sent": False, "message": f"Resend failed: {str(e)}"}
    
    # --- NO EMAIL CONFIGURED (dev mode) ---
    return {"sent": False, "message": "No email service configured. Set SMTP_USER/SMTP_APP_PASSWORD or RESEND_API_KEY."}