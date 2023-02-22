"""The ``app_logging`` module handles the configuration and execution of
application logging.

Module Contents
---------------
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ApplicationLog:
    """Configure and handle application logging tasks"""

    # Set the base logging level to log everything (level 0)
    # and apply additional filtering at the handler level
    app_logger = logging.getLogger('application_logger')
    app_logger.setLevel(0)

    file_logger = logging.getLogger('file_logger')
    file_logger.setLevel(0)

    console_logger = logging.getLogger('console_logger')
    console_logger.setLevel(0)

    # Remove the automatically generated handlers from each logger
    for logger in (app_logger, console_logger, file_logger):
        for handler in logger.handlers:
            logger.removeHandler(handler)

    console_format = logging.Formatter('%(levelname)8s - %(message)s')
    file_format = logging.Formatter('%(levelname)8s | %(asctime)s | %(message)s')

    @classmethod
    def configure_console(cls, level: Optional[int]) -> None:
        """Configure the logging level used when logging to the console

        If the logging level is None, then console logging is disabled.

        Args:
            level: The logging threshold to set
        """

        # Remove any old stream handlers
        for logger in (cls.app_logger, cls.console_logger):
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    logger.removeHandler(handler)

        if level is None:
            return

        # Create a new stream handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(cls.console_format)
        stream_handler.setLevel(level)

        # Add the stream handler to the appropriate loggers
        cls.app_logger.addHandler(stream_handler)
        cls.console_logger.addHandler(stream_handler)

    @classmethod
    def configure_log_file(cls, level: Optional[int], log_path: Path = None) -> None:
        """Configure logging to the application log file

        If the logging level is None, then console logging is disabled.

        Args:
            level: The logging threshold to set
            log_path: The path of the log file to use
        """

        # Remove any old file handlers
        for logger in (cls.app_logger, cls.file_logger):
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    logger.removeHandler(handler)

        if level is None:
            return

        # Create a new file handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(cls.file_format)
        file_handler.setLevel(level)

        # Add the file handler to the appropriate loggers
        cls.app_logger.addHandler(file_handler)
        cls.file_logger.addHandler(file_handler)

    @classmethod
    def log(cls, *args, **kwargs) -> None:
        """Write a log message to all configured destinations"""

        cls.app_logger.log(*args, **kwargs)

    @classmethod
    def log_to_console(cls, *args, **kwargs) -> None:
        """Write a log message only to the console"""

        cls.console_logger.log(*args, **kwargs)

    @classmethod
    def log_to_file(cls, *args, **kwargs) -> None:
        """Write a log message only to the log file"""

        cls.file_logger.log(*args, **kwargs)
