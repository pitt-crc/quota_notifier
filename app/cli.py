"""The ``cli`` module defines the application's command line interface and
serves as the primary entrypoint for executing the parent package.
It is responsible for displaying help text, parsing arguments, and
instantiating/executing the underlying application logic.

Module Contents
---------------
"""

from argparse import ArgumentParser
from pathlib import Path

from . import __version__
from .notify import UserNotifier
from .orm import DBConnection
from .settings import ApplicationSettings


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
        self.add_argument('-c', '--configure', required=False, type=Path, help='path to application settings file')


class Application:
    """Entry point for instantiating and executing the application from the command line"""

    @classmethod
    def execute(cls) -> None:
        """Parse arguments and execute the application"""

        args = Parser().parse_args()
        ApplicationSettings.configure_from_file(args.configure)
        DBConnection.configure()
        UserNotifier().send_notifications()
