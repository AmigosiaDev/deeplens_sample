"""
Email notification service.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from string import Template

from app.config import Config
from app.utils.helpers import format_currency

logger = logging.getLogger(__name__)

WELCOME_TEMPLATE = Template("""
Hello $name,

Welcome to $app_name! Your account has been created successfully.

Username: $username

Thanks for joining us!
""")

ORDER_TEMPLATE = Template("""
Hello $name,

Your order has been confirmed.

Order ID : $order_id
Total     : $total

We'll notify you when it ships.
""")


class EmailService:
    """Handles sending email notifications."""

    def __init__(self, config: Config):
        self.config = config
        self._sent: List[dict] = []  # in-memory log for testing

    def send_welcome_email(self, to_email: str, username: str, name: str) -> bool:
        """Send a welcome email to a newly registered user."""
        body = WELCOME_TEMPLATE.substitute(
            name=name or username,
            app_name=self.config.APP_NAME,
            username=username,
        )
        return self._send(to_email, subject=f"Welcome to {self.config.APP_NAME}!", body=body)

    def send_order_confirmation(
        self, to_email: str, name: str, order_id: str, total: float
    ) -> bool:
        """Send an order confirmation email."""
        body = ORDER_TEMPLATE.substitute(
            name=name,
            order_id=order_id,
            total=format_currency(total),
        )
        return self._send(to_email, subject=f"Order Confirmation - {order_id}", body=body)

    def _send(self, to: str, subject: str, body: str) -> bool:
        """Internal method to send an email via SMTP."""
        msg = MIMEMultipart()
        msg["From"] = self.config.EMAIL_USERNAME
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Log for testing / dev mode
        self._sent.append({"to": to, "subject": subject})

        if self.config.DEBUG:
            logger.debug(f"[DEBUG] Skipping SMTP. Email to {to}: {subject}")
            return True

        try:
            with smtplib.SMTP(self.config.EMAIL_HOST, self.config.EMAIL_PORT) as server:
                server.starttls()
                server.login(self.config.EMAIL_USERNAME, self.config.EMAIL_PASSWORD)
                server.send_message(msg)
            logger.info(f"Email sent to {to}: {subject}")
            return True
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    @property
    def sent_count(self) -> int:
        return len(self._sent)
