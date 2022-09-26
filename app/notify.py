"""The ``notify`` module contains the primary application logic for checking
disk quotas and issuing pending notifications.

Module Contents
---------------
"""

import pwd
from bisect import bisect_right
from typing import Iterable, Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from .disk_utils import AbstractQuota, QuotaFactory
from .email import EmailTemplate
from .orm import DBConnection, Notification
from .settings import ApplicationSettings
from .shell import User


class UserNotifier:
    """Issue and manage user disk quota notifications"""

    @staticmethod
    def get_users() -> Iterable[User]:
        """Return a collection of users to check quotas for

        Returns:
            A tuple of ``User`` objects
        """

        return (User(entry.pw_name) for entry in pwd.getpwall())

    @staticmethod
    def get_user_quotas(user: User) -> Iterable[AbstractQuota]:
        """Return a tuple of quotas assigned to a given user

        Args:
            user: The user to fetch quotas for

        Returns:
            A (possibly empty) tuple of quota objects
        """

        all_quotas = (QuotaFactory(**file_sys, user=user) for file_sys in ApplicationSettings['file_systems'])
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
        if db_entry := session.execute(query).scalars().first():
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
        thresholds: list[int] = ApplicationSettings['thresholds']
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

        with DBConnection.session() as session:
            for quota in self.get_user_quotas(user):
                last_threshold = self.get_last_threshold(session, quota)
                next_threshold = self.get_next_threshold(quota)

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
                elif last_threshold is None:
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
            EmailTemplate(quotas_to_notify).send_to_user(user)

        # Wait to commit until the email sends
        session.commit()

    def send_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold"""

        for user in self.get_users():
            self.notify_user(user)
