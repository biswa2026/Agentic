import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_email_gmail(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = None
):
    try:
        if not GMAIL_USER or not GMAIL_APP_PASSWORD:
            raise Exception("GMAIL_USER or GMAIL_APP_PASSWORD not set in environment variables")

        if from_email is None:
            from_email = GMAIL_USER

        msg = EmailMessage()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # Plain-text fallback
        msg.set_content("This email requires an HTML-compatible email client.")

        # HTML content
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"📧 Email successfully sent to {to_email}")

    except Exception as e:
        print(f"❌ Gmail SMTP error sending to {to_email}: {str(e)}")
