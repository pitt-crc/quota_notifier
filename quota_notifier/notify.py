"""The ``notify`` module contains the primary application logic for checking
disk quotas and issuing pending notifications.

Module Contents
---------------
"""

import logging
import pwd
from bisect import bisect_right
from typing import Iterable, Optional, Tuple

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from .disk_utils import AbstractQuota, BeegfsQuota, QuotaFactory
from .email import EmailTemplate
from .orm import DBConnection, Notification
from .settings import ApplicationSettings
from .shell import User


class UserNotifier:
    """Issue and manage user disk quota notifications"""

    @staticmethod
    def get_users() -> Tuple[User]:
        """Return a collection of users to check quotas for

        Returns:
            A iterable collection of ``User`` objects
        """

        logging.info('Fetching user list...')

        user_data = pwd.getpwall()
        blacklist = ApplicationSettings.get('blacklist')
        users = tuple(User(entry.pw_name) for entry in user_data if entry.pw_name not in blacklist)

        logging.debug(f'Found {len(users)}/{len(user_data)} non-blacklisted users')
        return users

    @staticmethod
    def get_user_quotas(user: User) -> Iterable[AbstractQuota]:
        """Return a tuple of quotas assigned to a given user

        Args:
            user: The user to fetch quotas for

        Returns:
            An iterable collection of quota objects
        """

        all_quotas = (QuotaFactory(**file_sys, user=user) for file_sys in ApplicationSettings.get('file_systems'))
        return filter(None, all_quotas)

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
            if not ApplicationSettings.get('debug'):
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
                logging.info(f'Caching quota info for {file_system.path}')
                BeegfsQuota.cache_quotas(name=file_system.name, path=file_system.path, users=users)

        if not cachable_systems_found:
            logging.debug('No cachable system queries found')

        logging.info('Scanning user quotas...')
        for user in users:
            self.notify_user(user)
