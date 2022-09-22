"""The ``notify`` module contains the primary application logic for checking
disk quotas and issuing pending notifications.

Module Contents
---------------
"""
from typing import Optional

from .disk_utils import AbstractQuota, QuotaFactory
from .email import EmailTemplate
from .orm import DBConnection
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

    def get_next_threshold(self, quota: AbstractQuota) -> Optional[int]:
        """Return the next threshold a user should be notified for

        Args:
            quota: The quota to get a threshold for

        Returns:
            A notification threshold between 0 and 100 (inclusive)
        """

        with DBConnection.session() as session:
            ...
            # Get notification history for user
            # If usage has dropped below threshold, update the record and return none
            # If there is a next threshold, return it

        # return none

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

    def notify_user(self, user: User) -> None:
        """Send email notifications to a single user

        Args:
            user: The user to send a notification to
        """

        pending_notifications = []
        for quota in self.get_user_quotas(user):
            next_threshold = self.get_next_threshold(quota)
            usage = (quota.size_used * 100) // quota.size_limit
            if next_threshold and usage >= next_threshold:
                pending_notifications.append(quota)

        if pending_notifications:
            EmailTemplate(pending_notifications).send_to_user(user)

    def send_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold"""

        for user in self.get_users():
            self.notify_user(user)
