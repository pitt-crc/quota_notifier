"""Tests for the ``Application`` class."""

import logging
from argparse import Namespace
from json import JSONDecodeError
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from quota_notifier.main import Application, DEFAULT_SETTINGS_PATH
from quota_notifier.orm import DBConnection
from quota_notifier.settings import ApplicationSettings


class SettingsValidation(TestCase):
    """Test the validation of application settings files when ``validate=True``"""

    def test_error_missing_file(self) -> None:
        """Test ``FileNotFoundError`` is raised when the settings file does not exist"""

        args = Namespace(validate=True, verbose=0, debug=False, settings=Path('fake/file/path.json'))
        with self.assertRaises(FileNotFoundError):
            Application.run(args)

    def test_error_on_empty_file(self) -> None:
        """Test ``JSONDecodeError`` is raised when the settings file is empty"""

        with self.assertRaises(JSONDecodeError), NamedTemporaryFile() as temp:
            args = Namespace(validate=True, verbose=0, debug=False, settings=Path(temp.name))
            Application.run(args)

    @staticmethod
    def test_no_error_on_defaults() -> None:
        """Test no error is raised when validating default application settings"""

        args = Namespace(validate=True, verbose=0, debug=False, settings=DEFAULT_SETTINGS_PATH)
        Application.run(args)


class LoggingConfiguration(TestCase):
    """Test the configuration of application logging"""

    def setUp(self) -> None:
        """Reset any existing logging configuration to defaults

        Prevents application state from bleeding over from other tests.
        """

        root = logging.getLogger()
        list(map(root.removeHandler, root.handlers[:]))
        list(map(root.removeFilter, root.filters[:]))

    def test_verbose_level_zero(self):
        """Test setting ``verbose=0`` blocks all logging"""

        Application.execute([])
        self.assertEqual(100, logging.getLogger().level)

    def test_verbose_level_one(self):
        """Test setting ``verbose=1`` sets the logging level to ``WARNING``"""

        Application.execute(['-v'])
        self.assertEqual(logging.WARNING, logging.getLogger().level)

    def test_verbose_level_two(self):
        """Test setting ``verbose=2`` sets the logging level to ``INFO``"""

        Application.execute(['-vv'])
        self.assertEqual(logging.INFO, logging.getLogger().level)

    def test_verbose_level_three(self):
        """Test setting ``verbose=3`` sets the logging level to ``DEBUG``"""

        Application.execute(['-vvv'])
        self.assertEqual(logging.DEBUG, logging.getLogger().level)

    def test_verbose_level_many(self):
        """Test setting ``verbose`` to a very high number sets the logging level to ``DEBUG``"""

        Application.execute(['-vvvvvvvvvv'])
        self.assertEqual(logging.DEBUG, logging.getLogger().level)


class DatabaseConfiguration(TestCase):
    """Test configuration of the application database"""

    def test_db_in_memory(self) -> None:
        """Test debug mode forces an in-memory database"""

        Application.execute(['--debug'])
        self.assertEqual('sqlite:///:memory:', DBConnection.url)

    def test_db_matches_default_settings(self) -> None:
        """Test the memory URL defaults to the default application settings"""

        Application.execute([])
        self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)
