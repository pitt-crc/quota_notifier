"""The ``notify`` module contains the primary application logic for checking
disk quotas and issuing pending email notifications.

Module Contents
---------------
"""

import logging
import pwd
from bisect import bisect_right
from email.message import EmailMessage
from smtplib import SMTP
from typing import Collection, Optional
from typing import Iterable, Tuple

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from quota_notifier.disk_utils import AbstractQuota
from quota_notifier.settings import ApplicationSettings
from quota_notifier.shell import User
from .disk_utils import BeeGFSQuota, QuotaFactory
from .orm import DBConnection, Notification


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


class UserNotifier:
    """Issue and manage user disk quota notifications"""

    @staticmethod
    def get_users() -> Iterable[User]:
        """Return a collection of users to check quotas for

        Returns:
            A iterable collection of ``User`` objects
        """

        logging.info('Fetching user list...')

        all_users = pwd.getpwall()
        user_blacklist = ApplicationSettings.get('blacklist')
        group_blacklist = ApplicationSettings.get('group_blacklist')

        allowed_users = []
        for user_entry in all_users:
            user = User(user_entry.pw_name)
            if user.username not in user_blacklist and user.group not in group_blacklist:
                allowed_users.append(user)

        logging.debug(f'Found {len(allowed_users)}/{len(all_users)} non-blacklisted users')
        return all_users

    @staticmethod
    def get_user_quotas(user: User) -> Iterable[AbstractQuota]:
        """Return a tuple of quotas assigned to a given user

        Args:
            user: The user to fetch quotas for

        Returns:
            An iterable collection of quota objects
        """

        for file_sys in ApplicationSettings.get('file_systems'):
            user_path = file_sys.path
            if file_sys.type == 'generic':
                user_path /= user.group

            quota = QuotaFactory(quota_type=file_sys.type, name=file_sys.name, path=user_path, user=user)
            if quota:
                yield quota

    @staticmethod
    def get_last_threshold(session: Session, quota: AbstractQuota) -> Optional[int]:
        """Return the last threshold a user was notified for

        Args:
            session: Active database session for performing select queries
            quota: The quota to get a threshold for

        Returns:
            The last notification or None if there was no notification
        """

        query = select(Notification).where(
            Notification.username == quota.user.username,
            Notification.file_system == quota.name)

        last_notification = None
        db_entry = session.execute(query).scalars().first()
        if db_entry:
            last_notification = db_entry.threshold

        return last_notification

    @staticmethod
    def get_next_threshold(quota: AbstractQuota) -> Optional[int]:
        """Return the next threshold a user should be notified for

        Args:
            quota: The quota to get a threshold for

        Returns:
            The largest notification threshold that is less than the current usage or None
        """

        next_threshold = None
        thresholds = ApplicationSettings.get('thresholds')
        if quota.percentage >= min(thresholds):
            index = bisect_right(thresholds, quota.percentage)
            next_threshold = thresholds[index - 1]

        return next_threshold

    def notify_user(self, user: User) -> None:
        """Send any pending email notifications the given user

        Args:
            user: The user to send a notification to
        """

        quotas_to_notify = []  # Track which quotas need email notifications

        logging.debug(f'Checking quotas for {user}...')
        with DBConnection.session() as session:
            for quota in self.get_user_quotas(user):
                next_threshold = self.get_next_threshold(quota)
                last_threshold = self.get_last_threshold(session, quota)

                # Usage is below the lowest threshold
                # Clean up the DB and continue
                if next_threshold is None:
                    session.execute(
                        delete(Notification).where(
                            Notification.username == user.username,
                            Notification.file_system == quota.name
                        )
                    )

                # There was no previous notification
                # Mark the quota as needing a notification and create a DB record
                elif last_threshold is None or next_threshold > last_threshold:
                    quotas_to_notify.append(quota)
                    session.execute(
                        insert(Notification).values(
                            username=user.username,
                            file_system=quota.name,
                            threshold=next_threshold
                        )
                    )

                # Quota usage dropped to a lower threshold
                # Update the DB and do not issue a notification
                elif next_threshold <= last_threshold:
                    session.execute(
                        insert(Notification).values(
                            username=user.username,
                            file_system=quota.name,
                            threshold=next_threshold
                        )
                    )

            # Issue email notification if necessary
            if quotas_to_notify:
                logging.info(f'{user} has {len(quotas_to_notify)} pending notifications')
                EmailTemplate(quotas_to_notify).send_to_user(user)

            else:
                logging.debug(f'{user} has no quotas pending notification')

            # Wait to commit until the email sends
            session.commit()

    def send_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold"""

        users = self.get_users()

        # Cache queries for BeeGFS file systems
        logging.info('Checking for cachable file system queries...')
        cachable_systems_found = False

        for file_system in ApplicationSettings.get('file_systems'):
            if file_system.type == 'beegfs':
                cachable_systems_found = True
                BeeGFSQuota.cache_quotas(name=file_system.name, path=file_system.path, users=users)

        if not cachable_systems_found:
            logging.debug('No cachable system queries found')

        logging.info('Scanning user quotas...')
        for user in users:
            self.notify_user(user)
