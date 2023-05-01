"""The application commandline interface.

This module defines the application's command line interface
and serves as the primary entrypoint for executing the parent package.
It is responsible for parsing arguments, configuring the application,
and instantiating/executing the underlying application logic.

Module Contents
---------------
"""

import logging
import logging.config
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from . import __version__
from .notify import UserNotifier
from .orm import DBConnection
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

    @staticmethod
    def _load_settings(force_debug: bool = False) -> None:
        """Load application settings from the given file path

        Args:
            force_debug: Force the application to run in debug mode
        """

        # Load and validate custom application settings from disk
        # Implicitly raises an error if settings are invalid
        if SETTINGS_PATH.exists():
            ApplicationSettings.set_from_file(SETTINGS_PATH)

        # Force debug mode if specified
        if force_debug:
            ApplicationSettings.set(debug=True)

    @classmethod
    def _configure_logging(cls, console_log_level: int) -> None:
        """Configure python logging to the given level

        Args:
            console_log_level: Logging level to set console logging to
        """

        # Logging levels are set at the handler level instead of the logger level
        # This allows more flexible usage of the root logger

        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'console_formatter': {
                    'format': '%(levelname)8s: %(message)s'
                },
                'log_file_formatter': {
                    'format': '%(levelname)8s | %(asctime)s | %(message)s'
                },
            },
            'handlers': {
                'console_handler': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'console_formatter',
                    'level': console_log_level
                },
                'log_file_handler': {
                    'class': 'logging.FileHandler',
                    'formatter': 'log_file_formatter',
                    'level': ApplicationSettings.get('log_level'),
                    'filename': ApplicationSettings.get('log_path')
                }
            },
            'loggers': {
                'console_logger': {'handlers': ['console_handler'], 'level': 0, 'propagate': False},
                'file_logger': {'handlers': ['log_file_handler'], 'level': 0, 'propagate': False},
                '': {'handlers': ['console_handler', 'log_file_handler'], 'level': 0, 'propagate': False},
            }
        })

    @classmethod
    def _configure_database(cls) -> None:
        """Configure the application database connection"""

        if ApplicationSettings.get('debug'):
            DBConnection.configure('sqlite:///:memory:')

        else:
            DBConnection.configure(ApplicationSettings.get('db_url'))

    @classmethod
    def run(cls, validate: bool = False, verbosity: int = 0, debug: bool = False) -> None:
        """Run the application using parsed commandline arguments

        Args:
            validate: Validate application settings without issuing user notifications
            verbosity: Console output verbosity
            debug: Run the application in debug mode
        """

        # Configure application settings
        cls._load_settings(force_debug=debug)
        if validate:
            return

        # Map number of verbosity flags to logging levels
        log_levels = {
            0: logging.ERROR,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG}

        # Configure application logging (to console and file)
        cls._configure_logging(console_log_level=log_levels.get(verbosity, logging.DEBUG))
        if ApplicationSettings.get('debug'):
            logging.warning('Running application in debug mode')

        # Connect to the database and run the core application logic
        cls._configure_database()
        UserNotifier().send_notifications()

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
                verbosity=args.verbose,
                debug=args.debug)

        except Exception as caught:
            logging.getLogger('file_logger').critical('Application crash', exc_info=caught)
            logging.getLogger('console_logger').critical(str(caught))

        else:
            logging.info('Exiting application gracefully')
