"""The ``notify`` module contains the primary application logic for checking
disk quotas and issuing pending notifications.

Module Contents
---------------
"""
from bisect import bisect_right

from sqlalchemy import select, update

from .disk_utils import AbstractQuota, QuotaFactory
from .email import EmailTemplate
from .orm import DBConnection, Notification
from .settings import app_settings
from .shell import User


class UserNotifier:
    """Issue and manage user disk quota notifications"""

    @staticmethod
    def get_users() -> tuple[User]:
        """Return a collection of users to check quotas for

        Returns:
            A tuple of ``User`` objects
        """

        # When implementing this function remember to drop names from the blacklist
        # app_settings.blacklist

        raise NotImplementedError

    @staticmethod
    def get_user_quotas(user: User) -> tuple[AbstractQuota]:
        """Return a tuple of quotas assigned to a given user

        Args:
            user: The user to fetch quotas for

        Returns:
            A (possibly empty) tuple of quota objects
        """

        all_quotas = (QuotaFactory(**quota_definition, user=user) for quota_definition in app_settings)
        return tuple(filter(None, all_quotas))

    def get_next_threshold(self, quota: AbstractQuota) -> int:
        """Return the next threshold a user should be notified for

        Args:
            quota: The quota to get a threshold for

        Returns:
            - The last notification or None if there was no notification
            - The next notification threshold or None if not needed
        """

        with DBConnection.session() as session:
            query = select(Notification).where(username=quota.user.username, file_system=quota.name)
            db_entry: Notification = session.execute(query).scalars().first()

            if not db_entry:
                return app_settings.thresholds[0], bisect_right(app_settings.thresholds, db_entry.threshold)

            return app_settings.thresholds, bisect_right(app_settings.thresholds, db_entry.threshold)

    def notify_user(self, user: User) -> None:
        """Send email notifications to a single user

        Args:
            user: The user to send a notification to
        """

        quotas = self.get_user_quotas(user)
        pending_notifications = False

        with DBConnection.session() as session:
            for quota in quotas:
                check_threshold, new_threshold = self.get_next_threshold(quota)
                if quota.percentage >= check_threshold:
                    pending_notifications = True

                session.execute(
                    update(Notification).where(username=user.username).where(file_system=quota.name).set(threshold=new_threshold)
                )

            if pending_notifications:
                EmailTemplate(quotas).send_to_user(user)

            session.commit()

    def send_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold"""

        for user in self.get_users():
            self.notify_user(user)
