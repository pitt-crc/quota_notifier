"""Tests for the ``Application`` class."""

import logging
from argparse import Namespace
from json import JSONDecodeError
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from quota_notifier.main import Application, DEFAULT_SETTINGS
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

        args = Namespace(validate=True, verbose=0, debug=False, settings=DEFAULT_SETTINGS)
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

    def test_logging_format_set(self):
        """Test the logging format is configured"""

        args = Namespace(validate=False, verbose=0, debug=False, settings=DEFAULT_SETTINGS)
        Application.run(args)

        log_format = logging.getLogger().handlers[0].formatter._fmt
        self.assertEqual('%(levelname)8s - %(message)s', log_format)

    def test_logging_level_zero(self):
        """Test settings the logging level to ``verbose=0``"""

        args = Namespace(validate=False, verbose=0, debug=False, settings=DEFAULT_SETTINGS)
        Application.run(args)
        self.assertEqual(100, logging.getLogger().level)

    def test_logging_level_one(self):
        """Test settings the logging level to ``verbose=1``"""

        args = Namespace(validate=False, verbose=1, debug=False, settings=DEFAULT_SETTINGS)
        Application.run(args)
        self.assertEqual(logging.INFO, logging.getLogger().level)

    def test_logging_level_two(self):
        """Test settings the logging level to ``verbose=2``"""

        args = Namespace(validate=False, verbose=2, debug=False, settings=DEFAULT_SETTINGS)
        Application.run(args)
        self.assertEqual(logging.DEBUG, logging.getLogger().level)

    def test_error_invalid_level(self):
        """Test an error is raised for an invalid verbose level"""

        with self.assertRaises(ValueError):
            args = Namespace(validate=False, verbose=5, debug=False, settings=DEFAULT_SETTINGS)
            Application.run(args)


class DatabaseConfiguration(TestCase):
    """Test configuration of the application database"""

    def test_db_in_memory(self) -> None:
        """Test debug mode forces an in-memory database"""

        args = Namespace(validate=False, verbose=0, debug=True, settings=DEFAULT_SETTINGS)
        Application.run(args)

        self.assertEqual('sqlite:///:memory:', DBConnection.url)

    def test_db_matches_url_matches_settings(self) -> None:
        """Test debug mode forces an in-memory database"""

        args = Namespace(validate=False, verbose=0, debug=False, settings=DEFAULT_SETTINGS)
        Application.run(args)

        self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)
