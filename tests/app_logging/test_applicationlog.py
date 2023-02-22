"""Tests for the ``ApplicationLogging`` class"""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from quota_notifier.app_logging import ApplicationLog


class ConfigureConsoleLogging(TestCase):
    """Test the configuration of logging to the console"""

    def test_has_handler(self):
        """Test exactly one logging handler is assigned to the logger"""

        # Configuring multiple times should only produce one handler
        ApplicationLog.configure_console(level=10)
        ApplicationLog.configure_console(level=10)

        handlers = ApplicationLog.console_logger.handlers
        self.assertEqual(1, len(handlers), f'Expected 1 handler, found {len(handlers)}: {handlers}')
        self.assertIsInstance(handlers[0], logging.StreamHandler)

    def test_handler_level_set(self) -> None:
        """Test the appropriate log level is set for the logging handler"""

        for log_level in (0, 10, 20, 30, 40, 50):
            ApplicationLog.configure_console(level=log_level)
            for handler in ApplicationLog.console_logger.handlers:
                self.assertEqual(log_level, handler.level)

    def test_logging_level_none(self) -> None:
        """Test logging is disabled when the logging level is None"""

        ApplicationLog.configure_console(level=None)
        self.assertFalse(ApplicationLog.console_logger.handlers)

    def test_handler_assigned_to_app_logger(self) -> None:
        """Test console log handlers are also assigned to the application log"""

        ApplicationLog.configure_console(level=10)
        for handler in ApplicationLog.console_logger.handlers:
            self.assertIn(handler, ApplicationLog.app_logger.handlers)

    def test_logging_format(self):
        """Test the console logging format has been customized to match the class ``console_format`` attribute"""

        ApplicationLog.configure_console(level=10)
        self.assertEqual(ApplicationLog.console_format, ApplicationLog.console_logger.handlers[0].formatter)


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
        ApplicationLog.configure_log_file(level=10, log_path=self.temp_file_path)
        ApplicationLog.configure_log_file(level=10, log_path=self.temp_file_path)

        handlers = ApplicationLog.file_logger.handlers
        self.assertEqual(1, len(handlers), f'Expected 1 handler, found {len(handlers)}: {handlers}')
        self.assertIsInstance(handlers[0], logging.FileHandler)

    def test_handler_level_set(self) -> None:
        """Test the appropriate log level is set for the logging handler"""

        for log_level in (0, 10, 20, 30, 40, 50):
            ApplicationLog.configure_log_file(log_level, self.temp_file_path)
            for handler in ApplicationLog.file_logger.handlers:
                self.assertEqual(log_level, handler.level)

    def test_logging_level_none(self) -> None:
        """Test logging is disabled when the logging level is None"""

        ApplicationLog.configure_log_file(level=None)
        self.assertFalse(ApplicationLog.file_logger.handlers)

    def test_handler_assigned_to_app_logger(self) -> None:
        """Test console log handlers are also assigned to the application log"""

        ApplicationLog.configure_log_file(level=10, log_path=self.temp_file_path)
        for handler in ApplicationLog.file_logger.handlers:
            self.assertIn(handler, ApplicationLog.app_logger.handlers)

    def test_logging_format(self):
        """Test the file logging format has been customized to match the class ``file_format`` attribute"""

        ApplicationLog.configure_log_file(level=10, log_path=self.temp_file_path)
        self.assertEqual(ApplicationLog.file_format, ApplicationLog.file_logger.handlers[0].formatter)
