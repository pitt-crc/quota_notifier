"""The ``main`` module defines the application's command line interface and
serves as the primary entrypoint for executing the parent package.
It is responsible for displaying help text, parsing arguments, and
instantiating/executing the underlying application logic.

Module Contents
---------------
"""

from argparse import ArgumentParser

from . import __version__
from .notify import UserNotifier


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
        notify.set_defaults(action=UserNotifier.send_notifications)


class Application:
    """Entry point for instantiating and executing the application from the command line"""

    @classmethod
    def execute(cls) -> None:
        """Parse arguments and execute the application"""

        args = vars(Parser().parse_args())
        args.pop('action')(UserNotifier(), **args)
