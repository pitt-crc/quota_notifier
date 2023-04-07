"""Tests for the ``Application`` class."""

import logging
import os
from pathlib import Path
from unittest import TestCase

from quota_notifier.cli import Application
from quota_notifier.orm import DBConnection
from quota_notifier.settings import ApplicationSettings
from tests.base import DefaultSetupTeardown


class ConsoleLogging(DefaultSetupTeardown, TestCase):
    """Test the application verbosity is set to match commandline arguments"""

    def test_logger_has_stream_handler(self) -> None:
        """Test the console logger has a single ``StreamHandler``"""

        Application.execute(['--debug'])
        handlers = logging.getLogger('console_logger').handlers

        self.assertEqual(1, len(handlers))
        self.assertIsInstance(handlers[0], logging.StreamHandler)

    def test_root_logs_to_console(self) -> None:
        """Test all console log handlers are included in the root logger"""

        for handler in logging.getLogger('console_logger').handlers:
            self.assertIn(handler, logging.getLogger().handlers)

    def _assert_console_logging_level(self, level: int) -> None:
        """Assert the handlers for the console logger are set to the given value

        Args:
            level: Logging level to test for at the handler level
        """

        logger = logging.getLogger('console_logger')
        self.assertEqual(0, logger.level, 'Logging level should be zero at the logger level')

        for handler in logger.handlers:
            self.assertEqual(level, handler.level, f'Handler logging level does no equal {logging.getLevelName(level)}')

    def test_verbose_level_zero(self):
        """Test the application defaults to logging errors and above in the console"""

        Application.execute(['--debug'])
        self._assert_console_logging_level(logging.ERROR)

    def test_verbose_level_one(self):
        """Test a single verbose flag sets the logging level to ``WARNING``"""

        Application.execute(['-v', '--debug'])
        self._assert_console_logging_level(logging.WARNING)

    def test_verbose_level_two(self):
        """Test two verbose flags sets the logging level to ``INFO``"""

        Application.execute(['-vv', '--debug'])
        self._assert_console_logging_level(logging.INFO)

    def test_verbose_level_three(self):
        """Test three verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvv', '--debug'])
        self._assert_console_logging_level(logging.DEBUG)

    def test_verbose_level_many(self):
        """Test several verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvvvvvvvvv', '--debug'])
        self._assert_console_logging_level(logging.DEBUG)


class FileLogging(DefaultSetupTeardown, TestCase):
    """Test the configuration for logging to file"""

    def test_logger_has_file_handler(self) -> None:
        """Test the file logger has a single ``FileHandler``"""

        Application.execute(['--debug'])
        handlers = logging.getLogger('file_logger').handlers

        self.assertEqual(1, len(handlers))
        self.assertIsInstance(handlers[0], logging.FileHandler)
        self.assertEqual(
            ApplicationSettings.get('log_path'),
            Path(handlers[0].baseFilename),
            'File handler path des not match application settings')

    def test_verbose_level_matches_settings(self) -> None:
        """Test the logging level for the log file matches application settings"""

        Application.execute(['--debug'])
        logger = logging.getLogger('file_logger')
        self.assertEqual(0, logger.level, 'Logging level should be zero at the logger level')

        for handler in logger.handlers:
            expected_level = ApplicationSettings.get('log_level')
            actual_level = logging.getLevelName(handler.level)
            self.assertEqual(expected_level, actual_level, 'Handler logging level does no match application settings')

    def test_root_logs_to_file(self) -> None:
        """Test all file log handlers are included in the root logger"""

        for handler in logging.getLogger('file_logger').handlers:
            self.assertIn(handler, logging.getLogger().handlers)


class DatabaseConfiguration(DefaultSetupTeardown, TestCase):
    """Test configuration of the application database"""

    def test_db_in_memory(self) -> None:
        """Test debug mode forces an in-memory database"""

        Application.execute(['--debug'])
        self.assertEqual('sqlite:///:memory:', DBConnection.url)

    def test_db_matches_default_settings(self) -> None:
        """Test the memory URL defaults to the default application settings"""

        Application.execute([])
        os.remove(ApplicationSettings.get('db_url').lstrip('sqlite:'))
        self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)
