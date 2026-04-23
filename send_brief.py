#!/usr/bin/env python3
import smtplib
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

SENDER = os.environ["EMAIL_SENDER"]
APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
RECIPIENT = os.environ.get("EMAIL_RECIPIENT", SENDER)


def send_brief(html_content: str) -> None:
    subject = f"🌅 Morning Market Note | {datetime.now().strftime('%B %d, %Y')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = RECIPIENT

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())

    print(f"Email sent successfully: {subject}")


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
