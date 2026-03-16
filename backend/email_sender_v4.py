"""
FireReach — Email Sender v4
Sends: text/plain email body + text/html brochure attachment
CAN-SPAM: List-Unsubscribe header on every email
"""

import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    # Fallback: load .env manually
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        pass

SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_APP_PASSWORD", "")

def send_with_brochure(
    to_email:      str,
    subject:       str,
    body:          str,
    brochure_html: str,
    company_name:  str,
    log:           list
) -> bool:
    """
    Send email with brochure as HTML attachment.
    Uses MIMEMultipart with 3 retries and exponential backoff.
    """
    max_retries = 3
    base_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            msg = MIMEMultipart("mixed")
            msg["Subject"]          = subject
            msg["From"]             = SMTP_USER
            msg["To"]               = to_email
            msg["List-Unsubscribe"] = f"<mailto:{SMTP_USER}?subject=unsubscribe>"

            # Part 1: short email body (plain text)
            body_part = MIMEText(body, "plain", "utf-8")
            msg.attach(body_part)

            # Part 2: brochure HTML attachment (safe truncation)
            # Truncate at last closing tag to avoid broken HTML
            if len(brochure_html) > 14000:
                last_close = brochure_html.rfind("</", 0, 14000)
                if last_close > 0:
                    # Find the end of this closing tag
                    tag_end = brochure_html.find(">", last_close)
                    if tag_end > 0:
                        brochure_trimmed = brochure_html[:tag_end + 1]
                    else:
                        brochure_trimmed = brochure_html[:14000]
                else:
                    brochure_trimmed = brochure_html[:14000]
            else:
                brochure_trimmed = brochure_html
                
            brochure_part = MIMEText(brochure_trimmed, "html", "utf-8")
            safe_name     = company_name.lower().replace(" ", "_").replace("/", "")[:20]
            brochure_part.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"{safe_name}_proposal.html"
            )
            msg.attach(brochure_part)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)

            log.append(f"[Send] Gmail SMTP → {to_email} (attempt {attempt + 1})")
            return True

        except smtplib.SMTPAuthenticationError:
            log.append("[Send] Auth failed — check SMTP_APP_PASSWORD")
            return False
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, ConnectionError) as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                log.append(f"[Send] Retry {attempt + 1}/{max_retries} in {delay}s: {str(e)}")
                time.sleep(delay)
                continue
            else:
                log.append(f"[Send] Failed after {max_retries} attempts: {str(e)}")
                return False
        except Exception as e:
            log.append(f"[Send] Failed: {e}")
            return False
    
    return False