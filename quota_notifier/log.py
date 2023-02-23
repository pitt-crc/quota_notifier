"""The ``app_logging`` module handles the configuration and execution of
application logging.

Three loggers are configured for logging to different locations.
The ``file_logger`` is used to log messages to the application log file.
The ``console_logger`` is used to log messages to STDOUT.
The default ``root`` logger will log to both the console and the log file.

Separate functions are provided for configuring the logging
threshold used when recording messages to each location.
Note that log levels are assigned at the handler level,
and not at the parent logger level.
This means the root logger will respect the logging thresholds configured
for each location.

Module Contents
---------------
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Type

root_logger = logging.getLogger()  # Default logger for logging everywhere
file_logger = logging.getLogger('file_logger')  # Logger for only the console
console_logger = logging.getLogger('console_logger')  # Logger for only the log file

# Don't propagate log messages to higher level loggers
file_logger.propagate = False
console_logger.propagate = False

# Format used for different logging destinations
console_format = logging.Formatter('%(levelname)8s: %(message)s')
file_format = logging.Formatter('%(levelname)8s | %(asctime)s | %(message)s')


def _remove_handlers(logger: logging.Logger, handler_type: Optional[Type[logging.Handler]] = None) -> None:
    """Remove all logging handlers from the given logger

    Args:
        logger: The logger to remove handlers from
        handler_type: Optionally only remove handlers of the given type
    """

    # Default to all handler object types
    handler_type = handler_type or object

    for handler in logger.handlers:
        if isinstance(handler, handler_type):
            logger.removeHandler(handler)


def configure_console(level: Optional[int]) -> None:
    """Configure the logging level used when logging to the console

    If the logging level is None, then console logging is disabled.

    Args:
        level: The logging threshold to set
    """

    _remove_handlers(console_logger)
    _remove_handlers(root_logger, logging.StreamHandler)

    if level is None:
        level = 1000

    for logger in (root_logger, console_logger,):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(console_format)
        stream_handler.setLevel(level)

        logger.addHandler(stream_handler)
        logger.setLevel(0)


def configure_log_file(level: Optional[int], log_path: Path = None) -> None:
    """Configure logging to the application log file

    If the logging level is None, then console logging is disabled.

    Args:
        level: The logging threshold to set
        log_path: The path of the log file to use
    """

    _remove_handlers(file_logger)
    _remove_handlers(root_logger, logging.FileHandler)

    if level is None:
        level = 1000

    for logger in (root_logger, file_logger):
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(file_format)
        file_handler.setLevel(level)

        logger.addHandler(file_handler)
        logger.setLevel(0)
