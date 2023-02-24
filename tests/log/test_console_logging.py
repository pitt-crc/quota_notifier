"""Tests for the configuring logging to the console"""

import logging
from unittest import TestCase

from quota_notifier.log import configure_console, console_logger, console_format


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
