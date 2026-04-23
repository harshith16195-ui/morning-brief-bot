#!/usr/bin/env python3
import smtplib
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def send_brief(html_content: str) -> None:
    SENDER = os.environ.get("EMAIL_SENDER")
    APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
    RECIPIENT = os.environ.get("EMAIL_RECIPIENT", SENDER)

    if not SENDER or not APP_PASSWORD:
        print(f"ERROR: Missing env vars. EMAIL_SENDER={SENDER}, EMAIL_APP_PASSWORD={'set' if APP_PASSWORD else 'MISSING'}", file=sys.stderr)
        sys.exit(1)

    subject = f"🗞️ Morning Market Note | {datetime.now().strftime('%B %d, %Y')}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(html_content, "html"))

    try:
        print(f"Connecting to Gmail SMTP...")
        import socket
        socket.setdefaulttimeout(30)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER, APP_PASSWORD)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
        print(f"Email sent successfully: {subject}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: Gmail auth failed - wrong app password? {e}", file=sys.stderr)
        sys.exit(1)
    except socket.timeout as e:
        print(f"ERROR: Connection timed out - Railway likely blocking port 465", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR sending email: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        html_content = sys.argv[1]
    else:
        brief_path = os.path.join(os.path.dirname(__file__), "brief_content.html")
        if not os.path.exists(brief_path):
            print(f"Error: No argument provided and {brief_path} not found.", file=sys.stderr)
            sys.exit(1)
        with open(brief_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    send_brief(html_content)

if __name__ == "__main__":
    main()
