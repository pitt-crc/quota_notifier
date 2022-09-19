"""Commandline interface and entrypoint for the parent package"""

from argparse import ArgumentParser

from . import __version__


class Parser(ArgumentParser):
    """Responsible for defining the commandline interface and parsing commandline arguments"""

    def __init__(self, *args, **kwargs) -> None:
        """Define arguments for the command line interface"""

        super().__init__(*args, **kwargs)
        self.subparsers = self.add_subparsers(parser_class=ArgumentParser, dest='action')
        self.subparsers.required = True

        self.description = 'Notify users when their disk usage passes predefined thresholds'
        self.add_argument('-v', '--version', action='version', version=__version__)

        notify = self.subparsers.add_parser('notify', help='Send emails to users with pending notifications')
        notify.set_defaults(action=Application.process_notifications)


class Application:
    """Entry point for instantiating and executing the application from the command line"""

    def send_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold

        Emails are only sent for a given user and threshold if a previous email
        has not already been issued.
        """

        raise NotImplementedError

    @classmethod
    def execute(cls) -> None:
        """Parse arguments and execute the application"""

        args = vars(Parser().parse_args())
        app = Application()
        args.pop('action')(app, **args)
