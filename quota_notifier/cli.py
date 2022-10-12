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
    def load_settings(settings_path: Path, error_on_missing_file: bool = False) -> None:
        """Load application settings from the given file path

        Args:
            settings_path: Path to the settings file
            error_on_missing_file: Optionally raise an error if ``settings_path`` does not exist

        Raises:
            FileNotFoundError: When the ``settings_path`` argument does not exist
        """

        # Load and validate custom application settings from disk
        # Implicitly raises an error if settings are invalid
        if settings_path.exists():
            ApplicationSettings.configure_from_file(settings_path)

        # If asked to validate a custom settings file that does not exist
        elif error_on_missing_file and settings_path != DEFAULT_SETTINGS:
            raise FileNotFoundError(f'No settings file at {settings_path}')

    @classmethod
    def run(cls, args: Namespace) -> None:
        """Run the application using parsed commandline arguments

        Args:
            args: Parsed commandline arguments
        """

        cls.load_settings(args.settings, error_on_missing_file=args.check)
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
