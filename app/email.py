"""Formattable email template for sending quota notifications to users."""

from email.message import EmailMessage
from smtplib import SMTP


class EmailTemplate:
    """Formattable email template to notify users about their quota"""

    def __init__(self, quotas):
        """Generate a formatted instance of the email template"""

        header = "This is an email header"
        footer = "This is a footer"

        quota_str = '\n'.join(map(str, quotas))
        self.message = '\n\n'.join((header, quota_str, footer))

    def send(self, to, from_, subject) -> None:
        """Send the formatted email to the given email address

        Args:
            to: Destination address
            from_: Sender address
            subject: Email subject line
        """

        email = EmailMessage()
        email.set_content(self.message)
        email["Subject"] = subject
        email["From"] = from_
        email["To"] = to

        with SMTP("localhost") as smtp:
            smtp.send_message(email)
