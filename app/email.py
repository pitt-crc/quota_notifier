"""Formattable email template for sending quota notifications to users.
By default, emails are sent via the SMTP server running on localhost.
"""

from email.message import EmailMessage
from smtplib import SMTP
from typing import Optional


class EmailTemplate:
    """Formattable email template to notify users about their quota"""

    header = "This is an email header"
    footer = "This is a footer"

    def __init__(self, quotas):
        """Generate a formatted instance of the email template"""

        quota_str = '\n'.join(map(str, quotas))
        self.message = '\n\n'.join((self.header, quota_str, self.footer))

    def send_to_user(
            self,
            user: str,
            address_from: str = "no-reply@crc.pitt.edu",
            subject: str = "CRC Disk Usage Update",
            smtp: Optional[SMTP] = None
    ) -> EmailMessage:
        """Send the formatted email to the given username

        Args:
            user: Name of the user to send to
            address_from: Sender address
            subject: Email subject line
            smtp: Optionally use a custom SMTP server
        """

        return self.send(address_to=f'{user}@pitt.edu', address_from=address_from, subject=subject, smtp=smtp)

    def send(self, address_to: str, address_from: str, subject: str, smtp: Optional[SMTP] = None) -> EmailMessage:
        """Send the formatted email to the given email address

        Args:
            address_to: Destination address
            address_from: Sender address
            subject: Email subject line
            smtp: Optionally use a custom SMTP server
        """

        email = EmailMessage()
        email.set_content(self.message)
        email["Subject"] = subject
        email["From"] = address_from
        email["To"] = address_to

        with smtp or SMTP("localhost") as smtp_server:
            smtp_server.send_message(email)

        return email
