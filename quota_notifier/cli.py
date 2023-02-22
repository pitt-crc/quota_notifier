"""The ``main`` module defines the application's command line interface
and serves as the primary entrypoint for executing the parent package.
It is responsible for parsing arguments, configuring the application,
and instantiating/executing the underlying application logic.

Module Contents
---------------
"""

import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from . import __version__
from .app_logging import ApplicationLog
from .notify import UserNotifier
from .settings import ApplicationSettings

SETTINGS_PATH = Path('/etc/notifier/settings.json')


class Parser(ArgumentParser):
    """Responsible for defining the commandline interface and parsing commandline arguments"""

    def __init__(
        self, *args,
        prog='notifier',
        description='Notify users when their disk usage passes predefined thresholds',
        **kwargs
    ) -> None:
        """Define arguments for the command line interface

        Args:
            prog: The name of the program displayed on the commandline
            description: Top level application description
            **kwargs: Any other arguments accepted by the ``ArgumentParser`` class
        """

        super().__init__(*args, prog=prog, description=description, **kwargs)
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('--validate', action='store_true', help='validate settings without sending notifications')
        self.add_argument('--debug', action='store_true', help='run the application but do not send any emails')
        self.add_argument(
            '-v', action='count', dest='verbose', default=0,
            help='set output verbosity to warning (-v), info (-vv), or debug (-vvv)')

    def error(self, message: str) -> None:
        """Exit the application and provide the given message"""

        raise SystemExit(f'{self.prog} error: {message}')


class Application:
    """Entry point for instantiating and executing the application"""

    @classmethod
    def _set_console_verbosity(cls, verbosity: int) -> None:
        """Set the output verbosity for console messages

        Args:
            verbosity: Number of commandline verbosity flags
        """

        log_level = {
            0: 100,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG
        }.get(verbosity, logging.DEBUG)

        ApplicationLog.configure_console(log_level)

    @staticmethod
    def _load_settings() -> None:
        """Load application settings from the given file path"""

        logging.info('Validating settings...')

        # Load and validate custom application settings from disk
        # Implicitly raises an error if settings are invalid
        if SETTINGS_PATH.exists():
            ApplicationSettings.set_from_file(SETTINGS_PATH)

        else:
            logging.info('Using default settings')

    @classmethod
    def run(cls, validate: bool = False, verbose: int = 0, debug: bool = False) -> None:
        """Run the application using parsed commandline arguments

        Args:
            validate: Validate application settings without issuing user notifications
            verbose: Console output verbosity
            debug: Run the application in debug mode
        """

        # Configure the application
        cls._set_console_verbosity(verbose)
        cls._load_settings()
        ApplicationSettings.set(debug=debug)

        # Run core application logic
        if not validate:
            UserNotifier().send_notifications()
            logging.info('Exiting application successfully')

    @classmethod
    def execute(cls, arg_list: List[str] = None) -> None:
        """Parse arguments and execute the application

        Raised exceptions are passed to STDERR via the argument parser.

        Args:
            arg_list: Run the application with the given arguments instead of parsing the command line
        """

        parser = Parser()
        args = parser.parse_args(arg_list)

        try:
            cls.run(
                validate=args.validate,
                verbose=args.verbose,
                debug=args.debug,
            )

        except Exception as caught:
            ApplicationLog.file_logger.exception(level=logging.CRITICAL)
            if not args.verbose:
                ApplicationLog.console_logger.critical(str(caught))
