"""The ``cli`` module defines the application's command line interface and
serves as the primary entrypoint for executing the parent package.
It is responsible for displaying help text, parsing arguments, and
instantiating/executing the underlying application logic.

Module Contents
---------------
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from . import __version__
from .notify import UserNotifier
from .orm import DBConnection
from .settings import ApplicationSettings

DEFAULT_SETTINGS = Path('/etc/notifier/settings.json')


class Parser(ArgumentParser):
    """Responsible for defining the commandline interface and parsing commandline arguments"""

    def __init__(
            self, *args,
            prog='notifier',
            description='Notify users when their disk usage passes predefined thresholds',
            **kwargs
    ) -> None:
        """Define arguments for the command line interface"""

        super().__init__(*args, prog=prog, description=description, **kwargs)
        self.add_argument('-v', '--version', action='version', version=__version__)
        self.add_argument('-s', '--settings', type=Path, default=DEFAULT_SETTINGS, help='path to application settings')
        self.add_argument('--check', action='store_true', help='validate app settings without sending notifications')


class Application:
    """Entry point for instantiating and executing the application from the command line"""

    @staticmethod
    def run(args: Namespace) -> None:
        """Run the application using parsed commandline arguments

        Args:
            args: Parsed commandline arguments

        Raises:
            FileNotFoundError: When the application settings file cannot be found
        """

        # Load application settings from disk and error on an invalid settings schema
        if args.settings.exists():
            ApplicationSettings.configure_from_file(args.settings)

        # Error if only checking the schema and no custom settings file exists
        elif args.check and args.settings != DEFAULT_SETTINGS:
            raise FileNotFoundError(f'No settings file at {args.settings}')

        if not args.check:
            DBConnection.configure()
            UserNotifier().send_notifications()

    @classmethod
    def execute(cls) -> None:
        """Parse arguments and execute the application

        Raised exceptions are passed to STDERR via the argument parser.
        """

        parser = Parser()
        args = parser.parse_args()

        try:
            cls.run(args)

        except Exception as caught:
            parser.error(str(caught))
