from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.common.models import SendEmail
from src.config import settings


class MailClient:
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.sender = "info@b-express.kz"
        self.sg = SendGridAPIClient(self.api_key)

    def send(self, send_email: SendEmail):
        message = Mail(
            from_email=self.sender,
            to_emails=send_email.email,
            subject=send_email.subject,
            html_content=send_email.message)
        response = self.sg.send(message)
        return response


mail_client = MailClient()
