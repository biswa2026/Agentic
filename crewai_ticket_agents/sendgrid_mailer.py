import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()


SENDGRID_API_KEY='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'


to_email='biswatripathy21@gmail.com'


def send_email_sendgrid(to_email, subject, html_content, from_email=None):
    try:
        sendgrid_key = SENDGRID_API_KEY

        if not sendgrid_key:
            raise Exception("SENDGRID_API_KEY not set in environment variables")

        if from_email is None:
            from_email = "biswatripathy21@gmail.com"   # default FROM address

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)

        print(f"📧 Email successfully sent to {to_email} ({response.status_code})")

    except Exception as e:
        print(f"❌ SendGrid Error sending to {to_email}: {str(e)}")
