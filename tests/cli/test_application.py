"""Tests for the ``Application`` class."""

import logging
import os
from unittest import TestCase

from quota_notifier.app_logging import ApplicationLog
from quota_notifier.cli import Application
from quota_notifier.orm import DBConnection
from quota_notifier.settings import ApplicationSettings


class VerbosityConfiguration(TestCase):
    """Test the application verbosity"""

    @classmethod
    def tearDownClass(cls) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    def test_output_format(self):
        """Test the console logging format has been customized"""

        Application.execute(['--debug', '-v', '--debug'])
        log_format = self.get_stream_handler().formatter._fmt
        self.assertEqual('%(levelname)8s - %(message)s', log_format)

    def test_verbose_level_zero(self):
        """Test the application is silent by default"""

        Application.execute(['--debug'])
        self.assertEqual(100, self.get_stream_handler().level)

    def test_verbose_level_one(self):
        """Test a single verbose flag sets the logging level to ``WARNING``"""

        Application.execute(['-v', '--debug'])
        self.assertEqual(logging.WARNING, self.get_stream_handler().level)

    def test_verbose_level_two(self):
        """Test two verbose flags sets the logging level to ``INFO``"""

        Application.execute(['-vv', '--debug'])
        self.assertEqual(logging.INFO, self.get_stream_handler().level)

    def test_verbose_level_three(self):
        """Test three verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvv', '--debug'])
        self.assertEqual(logging.DEBUG, self.get_stream_handler().level)

    def test_verbose_level_many(self):
        """Test several verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvvvvvvvvv', '--debug'])
        self.assertEqual(logging.DEBUG, self.get_stream_handler().level)


class DatabaseConfiguration(TestCase):
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
