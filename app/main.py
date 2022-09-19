"""Commandline interface and entrypoint for the parent package"""


class Application:
    """Entry point for instantiating and executing the application from the command line"""

    @classmethod
    def execute(cls):
        """Parse arguments and execute the application"""

        print('Hello World')
