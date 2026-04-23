#!/usr/bin/env python3
import sys
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

def send_brief(html_content: str) -> None:
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    SENDER = os.environ.get("EMAIL_SENDER")
    RECIPIENT = os.environ.get("EMAIL_RECIPIENT", SENDER)

    if not SENDGRID_API_KEY or not SENDER:
        print(f"ERROR: Missing env vars. SENDGRID_API_KEY={'set' if SENDGRID_API_KEY else 'MISSING'}, EMAIL_SENDER={SENDER}", file=sys.stderr)
        sys.exit(1)

    subject = f"Morning Market Note | {datetime.now().strftime('%B %d, %Y')}"

    message = Mail(
        from_email=SENDER,
        to_emails=RECIPIENT,
        subject=subject,
        html_content=html_content
    )

    try:
        print("Sending via SendGrid...")
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent successfully! Status: {response.status_code}")
    except Exception as e:
        print(f"ERROR sending email: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        html_content = sys.argv[1]
    else:
        brief_path = os.path.join(os.path.dirname(__file__), "brief_content.html")
        if not os.path.exists(brief_path):
            print(f"Error: {brief_path} not found.", file=sys.stderr)
            sys.exit(1)
        with open(brief_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    send_brief(html_content)

if __name__ == "__main__":
    main()
