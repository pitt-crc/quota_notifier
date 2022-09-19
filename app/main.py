"""Commandline interface and entrypoint for the parent package"""


class Application:
    """Entry point for instantiating and executing the application from the command line"""

    def process_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold

        Emails are only sent for a given user and threshold if a previous email
        has not already been issued.
        """

        raise NotImplementedError

    @classmethod
    def execute(cls):
        """Parse arguments and execute the application"""

        print('Hello World')
