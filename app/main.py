"""Commandline interface and entrypoint for the parent package"""

from argparse import ArgumentParser
from pathlib import Path

from . import __version__
from .disk_utils import AbstractQuota, BeegfsQuota, GenericQuota, IhomeQuota
from .email import EmailTemplate
from .shell import User


class Parser(ArgumentParser):
    """Responsible for defining the commandline interface and parsing commandline arguments"""

    def __init__(self, *args, **kwargs) -> None:
        """Define arguments for the command line interface"""

        super().__init__(*args, **kwargs)
        self.subparsers = self.add_subparsers(parser_class=ArgumentParser, dest='action')
        self.subparsers.required = True

        self.prog = 'notifier'
        self.description = 'Notify users when their disk usage passes predefined thresholds'
        self.add_argument('-v', '--version', action='version', version=__version__)

        notify = self.subparsers.add_parser('notify', help='Send emails to users with pending notifications')
        notify.set_defaults(action=Application.send_notifications)


class Application:
    """Entry point for instantiating and executing the application from the command line"""

    @staticmethod
    def _get_users() -> tuple[User]:
        """Return a collection of users to check quotas for

        Returns:
            A tuple of ``User`` objects
        """

        raise NotImplementedError

    def _get_next_threshold(self, quota: AbstractQuota) -> int:
        """Return the next threshold a user should be notified for

        Args:
            quota: The quota to get a threshold for

        Returns:
            A notification threshold between 0 and 100 (inclusive)
        """

        raise NotImplementedError

    @staticmethod
    def _get_user_quotas(user: User) -> tuple[AbstractQuota]:
        """Return a tuple of quotas assigned to a given user

        Args:
            user: The user to fetch quotas for

        Returns:
            A (possibly empty) tuple of quota objects
        """

        ihome_quota = IhomeQuota.from_uid('ihome', user.uid)
        zfs1_quota = GenericQuota.from_path('zfs1', Path(f'/zfs1/{user.group}'))
        zfs2_quota = GenericQuota.from_path('zfs2', Path(f'/zfs2/{user.group}'))
        bgfs_quota = BeegfsQuota.from_group('beegfs', user.group)
        ix_quota = GenericQuota.from_path('ix', Path(f'/ix/{user.group}'))
        ix1_quota = GenericQuota.from_path('ix1', Path(f'/ix1/{user.group}'))

        # Only return quotas that exist for the given group (i.e., objects that are not None)
        all_quotas = (ihome_quota, zfs1_quota, zfs2_quota, bgfs_quota, ix_quota, ix1_quota)
        return tuple(filter(None, all_quotas))

    def _notify_user(self, user: User) -> None:
        """Send email notifications to a single user

        Args:
            user: The user to send a notification for
        """

        pending_notifications = []
        for quota in self._get_user_quotas(user):
            next_threshold = self._get_next_threshold(quota)
            usage = (quota.size_used * 100) // quota.size_limit
            if usage >= next_threshold:
                pending_notifications.append(quota)

        if pending_notifications:
            EmailTemplate(pending_notifications).send_to_user(user)

    def send_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold"""

        for user in self._get_users():
            self._notify_user(user)

    @classmethod
    def execute(cls) -> None:
        """Parse arguments and execute the application"""

        args = vars(Parser().parse_args())
        app = Application()
        args.pop('action')(app, **args)
