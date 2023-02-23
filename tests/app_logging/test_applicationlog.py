"""Tests for the ``ApplicationLogging`` class"""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from quota_notifier.log import (
    configure_log_file,
    configure_console,
    console_logger,
    file_logger,
    console_format,
    file_format)


class ConfigureConsoleLogging(TestCase):
    """Test the configuration of logging to the console"""

    def test_has_handler(self):
        """Test exactly one logging handler is assigned to the logger"""

        # Configuring multiple times should only produce one handler
        configure_console(level=10)
        configure_console(level=10)

        handlers = console_logger.handlers
        self.assertEqual(1, len(handlers), f'Expected 1 handler, found {len(handlers)}: {handlers}')
        self.assertIsInstance(handlers[0], logging.StreamHandler)

    def test_handler_level_set(self) -> None:
        """Test the appropriate log level is set for the logging handler"""

        for log_level in (0, 10, 20, 30, 40, 50):
            configure_console(level=log_level)
            for handler in console_logger.handlers:
                self.assertEqual(log_level, handler.level)

    def test_logging_level_none(self) -> None:
        """Test logging is disabled when the logging level is None"""

        configure_console(level=None)
        for handler in console_logger.handlers:
            self.assertGreaterEqual(1000, handler.level)

    def test_logging_format(self):
        """Test the console logging format has been customized to match the class ``console_format`` attribute"""

        configure_console(level=10)
        self.assertEqual(console_format, console_logger.handlers[0].formatter)


class ConfigureFileLogging(TestCase):
    """Test the configuration of logging to the log file"""

    def setUp(self) -> None:
        """Create a temporary log file"""

        self._temp_file = NamedTemporaryFile(suffix='.log')
        self.temp_file_path = Path(self._temp_file.name)

    def tearDown(self) -> None:
        """Tear down the temporary log file"""

        self._temp_file.close()

    def test_has_handler(self):
        """Test exactly one logging handler is assigned to the logger"""

        # Configuring multiple times should only produce one handler
        configure_log_file(level=10, log_path=self.temp_file_path)
        configure_log_file(level=10, log_path=self.temp_file_path)

        handlers = file_logger.handlers
        self.assertEqual(1, len(handlers), f'Expected 1 handler, found {len(handlers)}: {handlers}')
        self.assertIsInstance(handlers[0], logging.FileHandler)

    def test_handler_level_set(self) -> None:
        """Test the appropriate log level is set for the logging handler"""

        for log_level in (0, 10, 20, 30, 40, 50):
            configure_log_file(log_level, self.temp_file_path)
            for handler in file_logger.handlers:
                self.assertEqual(log_level, handler.level)

    def test_logging_level_none(self) -> None:
        """Test logging is disabled when the logging level is None"""

        configure_log_file(level=None, log_path=self.temp_file_path)
        for handler in file_logger.handlers:
            self.assertGreaterEqual(1000, handler.level)

    def test_logging_format(self):
        """Test the file logging format has been customized to match the class ``file_format`` attribute"""

        configure_log_file(level=10, log_path=self.temp_file_path)
        self.assertEqual(file_format, file_logger.handlers[0].formatter)
