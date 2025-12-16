from sendgrid import SendGridAPIClient
import os
from dotenv import load_dotenv

load_dotenv()

sg = SendGridAPIClient(os.getenv("sendgrid_api"))

response = sg.client.user.profile.get()
print(response.status_code)
print(response.body)