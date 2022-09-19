"""Formattable email template for sending quota notifications to users."""

from email.message import EmailMessage
from smtplib import SMTP


class EmailTemplate:
    """Formattable email template to notify users about their quota"""

    header = "This is an email header"
    footer = "This is a footer"

    def __init__(self, quotas):
        """Generate a formatted instance of the email template"""

        quota_str = '\n'.join(map(str, quotas))
        self.message = '\n\n'.join((self.header, quota_str, self.footer))

    def send_to_user(self, user, from_="no-reply@crc.pitt.edu", subject="CRC Disk Usage Update"):
        """Send the formatted email to the given username

        Args:
            user: Name of the user to send to
            from_: Sender address
            subject: Email subject line
        """

        self.send(to=f'{user}@pitt.edu', from_=from_, subject=subject)

    def send(self, to, from_, subject, smtp) -> EmailMessage:
        """Send the formatted email to the given email address

        Args:
            to: Destination address
            from_: Sender address
            subject: Email subject line
            smtp: Optionally use a custom SMTP server
        """

        email = EmailMessage()
        email.set_content(self.message)
        email["Subject"] = subject
        email["From"] = from_
        email["To"] = to

        with  smtp or SMTP("localhost") as smtp_server:
            smtp_server.send_message(email)

        return email
