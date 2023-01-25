"""Tests for the ``Application`` class."""

import json
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

        args = Namespace(validate=True, verbose=0, debug=True, settings=Path('fake/file/path.json'))
        with self.assertRaises(FileNotFoundError):
            Application.run(args)

    def test_error_on_empty_file(self) -> None:
        """Test ``JSONDecodeError`` is raised when the settings file is empty"""

        with self.assertRaises(JSONDecodeError), NamedTemporaryFile() as temp:
            args = Namespace(validate=True, verbose=0, debug=True, settings=Path(temp.name))
            Application.run(args)

    @staticmethod
    def test_no_error_on_defaults() -> None:
        """Test no error is raised when validating default application settings"""

        args = Namespace(validate=True, verbose=0, debug=True, settings=DEFAULT_SETTINGS_PATH)
        Application.run(args)


class VerbosityConfiguration(TestCase):
    """Test the application verbosity"""

    def setUp(self) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    @classmethod
    def tearDownClass(cls) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    @staticmethod
    def get_stream_handler() -> logging.StreamHandler:
        """Return the ``StreamHandler`` instance used by the application when logging to the console"""

        handlers = [handler for handler in logging.getLogger().handlers if isinstance(handler, logging.StreamHandler)]
        if not handlers:
            raise RuntimeError('Stream handler not found')

        if len(handlers) > 1:
            raise RuntimeError('Multiple stream handlers found')

        return handlers[0]

    def test_output_format(self):
        """Test the console logging format has been customized"""

        Application.execute(['-v'])
        log_format = self.get_stream_handler().formatter._fmt
        self.assertEqual('%(levelname)8s - %(message)s', log_format)

    def test_verbose_level_zero(self):
        """Test the application is silent by default"""

        Application.execute([])
        with self.assertRaisesRegex(RuntimeError, 'Stream handler not found'):
            self.get_stream_handler()

    def test_verbose_level_one(self):
        """Test a single verbose flag sets the logging level to ``WARNING``"""

        Application.execute(['-v'])
        self.assertEqual(logging.WARNING, self.get_stream_handler().level)

    def test_verbose_level_two(self):
        """Test two verbose flags sets the logging level to ``INFO``"""

        Application.execute(['-vv'])
        self.assertEqual(logging.INFO, self.get_stream_handler().level)

    def test_verbose_level_three(self):
        """Test three verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvv'])
        self.assertEqual(logging.DEBUG, self.get_stream_handler().level)

    def test_verbose_level_many(self):
        """Test several verbose flags sets the logging level to ``DEBUG``"""

        Application.execute(['-vvvvvvvvvv'])
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

        # Remove the empty DB file generated automatically by application.execute
        Path(ApplicationSettings.get('db_url').lstrip('sqlite:')).unlink()

        self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)

    def test_db_matches_custom_settings(self) -> None:
        """Test the memory URL is updated to reflect custom application settings"""

        with NamedTemporaryFile(suffix='.db') as temp_db, NamedTemporaryFile(suffix='.json') as temp_settings:
            # Generate a custom settings file pointing at a custom DB path
            settings_str = json.dumps({'db_url': f'sqlite:///{temp_db.name}'})
            with open(temp_settings.name, 'w') as f:
                f.write(settings_str)

            # Check the DB url matches the custom DB path
            Application.execute(['-s', temp_settings.name])
            self.assertEqual(f'sqlite:///{temp_db.name}', DBConnection.url)
