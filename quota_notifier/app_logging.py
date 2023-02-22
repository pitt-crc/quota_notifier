import logging
import sys
from pathlib import Path
from typing import Optional


class ApplicationLog:
    # Set the root logging level to log everything
    # Apply additional filtering at the handler level
    _app_logger = logging.getLogger()
    _app_logger.setLevel(0)

    _file_logger = logging.getLogger('file_logger')
    _file_logger.setLevel(0)

    _console_logger = logging.getLogger('file_logger')
    _console_logger.setLevel(0)

    console_format = logging.Formatter('%(levelname)8s - %(message)s')
    file_format = logging.Formatter('%(levelname)8s | %(asctime)s | %(message)s')

    @classmethod
    def configure_console(cls, level: Optional[int]) -> None:

        # Remove any old stream handlers
        for logger in (cls._app_logger, cls._console_logger):
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
        cls._app_logger.addHandler(stream_handler)
        cls._console_logger.addHandler(stream_handler)

    @classmethod
    def configure_log_file(cls, level: Optional[int], log_path: Path = None) -> None:

        # Remove any old file handlers
        for logger in (cls._app_logger, cls._console_logger):
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
        cls._app_logger.addHandler(file_handler)
        cls._file_logger.addHandler(file_handler)

    @classmethod
    def log(cls, *args, **kwargs):
        cls._app_logger.log(*args, **kwargs)

    @classmethod
    def log_to_console(cls, *args, **kwargs):
        cls._console_logger.log(*args, **kwargs)

    @classmethod
    def log_to_file(cls, *args, **kwargs):
        cls._file_logger.log(*args, **kwargs)
