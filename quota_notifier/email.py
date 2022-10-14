"""The ``email`` module provides a formattable email template used to send
quota notifications to users. By default, emails are sent via the SMTP server
running on localhost.

Module Contents
---------------
"""
import logging
from email.message import EmailMessage
from smtplib import SMTP
from typing import Collection, Optional

from quota_notifier.disk_utils import AbstractQuota
from quota_notifier.settings import ApplicationSettings
from quota_notifier.shell import User


class EmailTemplate:
    """Formattable email template to notify users about their quota"""

    email_subject = ApplicationSettings.get('email_subject')
    email_from = ApplicationSettings.get('email_from')
    header = ApplicationSettings.get('email_header')
    footer = ApplicationSettings.get('email_footer')

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

        domain = ApplicationSettings.get('email_domain').lstrip('@')
        return self.send(address=f'{user.username}@{domain}', smtp=smtp)

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

        logging.debug(f'Sending email notification to {address}')
        if ApplicationSettings.get('debug'):
            return email

        with smtp or SMTP(
            host=ApplicationSettings.get('smtp_host'),
            port=ApplicationSettings.get('smtp_port')
        ) as smtp_server:
            smtp_server.send_message(email)

        return email
