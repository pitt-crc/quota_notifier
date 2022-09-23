"""The ``email`` module provides a formattable email template used to send
quota notifications to users. By default, emails are sent via the SMTP server
running on localhost.

Module Contents
---------------
"""

from email.message import EmailMessage
from smtplib import SMTP
from typing import Collection, Optional

from app.disk_utils import AbstractQuota
from app.settings import app_settings
from app.shell import User


class EmailTemplate:
    """Formattable email template to notify users about their quota"""

    email_subject = app_settings.email_subject
    email_from = app_settings.email_from
    header = app_settings.email_header
    footer = app_settings.email_footer

    def __init__(self, quotas: Collection[AbstractQuota]) -> None:
        """Generate a formatted instance of the email template"""

        quota_str = '\n'.join(map(str, quotas))
        self.message = '\n\n'.join((self.header, quota_str, self.footer))

    def send_to_user(self, user: User, smtp: Optional[SMTP] = None) -> EmailMessage:
        """Send the formatted email to the given username

        Args:
            user: Name of the user to send to
            smtp: Optionally use a custom SMTP server
        """

        return self.send(address=f'{user.username}@pitt.edu', smtp=smtp)

    def send(self, address: str, smtp: Optional[SMTP] = None) -> EmailMessage:
        """Send the formatted email to the given email address

        Args:
             address: Destination email address
            smtp: Optionally use a custom SMTP server
        """

        email = EmailMessage()
        email.set_content(self.message)
        email["Subject"] = self.email_subject
        email["From"] = self.email_from
        email["To"] = address

        with smtp or SMTP("localhost") as smtp_server:
            smtp_server.send_message(email)

        return email
