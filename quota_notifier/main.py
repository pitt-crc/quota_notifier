"""The ``main`` module defines the application's command line interface
and serves as the primary entrypoint for executing the parent package.
It is responsible for parsing arguments, configuring the application,
and instantiating/executing the underlying application logic.

Module Contents
---------------
"""

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from . import __version__
from .notify import UserNotifier
from .settings import ApplicationSettings

DEFAULT_SETTINGS_PATH = Path('/etc/notifier/settings.json')


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
            '-s', '--settings', type=Path, default=DEFAULT_SETTINGS_PATH,
            help='path to the application settings file')
        self.add_argument(
            '-v', action='count', dest='verbose', default=0,
            help='set output verbosity to warning (-v), info (-vv), or debug (-vvv)')


class Application:
    """Entry point for instantiating and executing the application"""

    @classmethod
    def _set_console_verbosity(cls, verbosity: int) -> None:
        """Set the output verbosity for console messages

        Args:
            verbosity: Number of commandline verbosity flags
        """

        # Set the root logging level to log everything
        # Apply additional filtering at the handler level
        app_logger = logging.getLogger()
        app_logger.setLevel(0)

        # Remove any old stream loggers
        for handler in app_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                app_logger.removeHandler(handler)

        log_format = logging.Formatter('%(levelname)8s - %(message)s')
        verbosity = {
            0: 100,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG
        }.get(verbosity, logging.DEBUG)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_format)
        stream_handler.setLevel(verbosity)
        app_logger.addHandler(stream_handler)

    @staticmethod
    def _load_settings(settings_path: Path) -> None:
        """Load application settings from the given file path

        Args:
            settings_path: Path to the settings file

        Raises:
            FileNotFoundError: When ``settings_path`` does not exist
        """

        logging.info('Validating settings...')

        # Load and validate custom application settings from disk
        # Implicitly raises an error if settings are invalid
        if settings_path.exists():
            ApplicationSettings.set_from_file(settings_path)

        # Raise an error if asked to validate a custom settings file that does not exist
        elif settings_path != DEFAULT_SETTINGS_PATH:
            logging.error(f'Custom settings file does not exist: {settings_path}')
            raise FileNotFoundError(f'No settings file at {settings_path}')

        # Load the default application settings
        else:
            logging.info('Using default settings')

    @classmethod
    def run(cls, settings: Path = None, validate: bool = False, verbose: int = 0, debug: bool = False) -> None:
        """Run the application using parsed commandline arguments

        Args:
            settings: Path to an application settings file
            validate: Validate application settings without issuing user notifications
            verbose: Console output verbosity
            debug: Run the application in debug mode
        """

        # Configure the application
        cls._set_console_verbosity(verbose)
        cls._load_settings(settings)
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
                settings=args.settings,
                validate=args.validate,
                verbose=args.verbose,
                debug=args.debug,
            )

        except Exception as caught:
            err_string = str(caught)
            logging.critical(err_string.replace('\n', ' '))

            # Avoid printing to stdout twice if verbose is enabled
            if not args.verbose:
                parser.error(err_string)
