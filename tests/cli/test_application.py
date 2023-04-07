"""Tests for the ``Application`` class."""

import logging
import os
from unittest import TestCase

from quota_notifier.cli import Application
from quota_notifier.orm import DBConnection
from quota_notifier.settings import ApplicationSettings


class ConsoleVerbosity(TestCase):
    """Test the application verbosity is set o match commandline arguments"""

    @classmethod
    def tearDownClass(cls) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    def test_verbose_level_zero(self):
        """Test the application defaults to logging errors and above in the console"""

        Application.execute(['--debug'])
        for handler in logging.getLogger('console_logger').handlers:
            self.assertEqual(logging.ERROR, handler.level)

    def test_verbose_level_one(self):
        """Test a single verbose flag sets the logging level to ``WARNING``"""

        Application.execute(['-v', '--debug'])
        for handler in logging.getLogger('console_logger').handlers:
            self.assertEqual(logging.WARNING, handler.level)

    def test_verbose_level_two(self):
        """Test two verbose flags sets the logging level to ``INFO``"""

        Application.execute(['-vv', '--debug'])
        for handler in logging.getLogger('console_logger').handlers:
            self.assertEqual(logging.INFO, handler.level)

    def test_verbose_level_three(self):
        """Test three verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvv', '--debug'])
        for handler in logging.getLogger('console_logger').handlers:
            self.assertEqual(logging.DEBUG, handler.level)

    def test_verbose_level_many(self):
        """Test several verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvvvvvvvvv', '--debug'])
        for handler in logging.getLogger('console_logger').handlers:
            self.assertEqual(logging.DEBUG, handler.level)


class DatabaseConfiguration(TestCase):
    """Test configuration of the application database"""

    def tearDown(self) -> None:
        """Restore default application settings

        These tests run the full application, including the configuration
        of application settings. As a result, settings need to be reset after
        each run.
        """

        ApplicationSettings.reset_defaults()

    def test_db_in_memory(self) -> None:
        """Test debug mode forces an in-memory database"""

        Application.execute(['--debug'])
        self.assertEqual('sqlite:///:memory:', DBConnection.url)

    def test_db_matches_default_settings(self) -> None:
        """Test the memory URL defaults to the default application settings"""

        Application.execute([])
        os.remove(ApplicationSettings.get('db_url').lstrip('sqlite:'))
        self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)
