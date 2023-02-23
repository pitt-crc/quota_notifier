"""Tests for the ``ApplicationSettings`` class"""

import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from pydantic import ValidationError

from quota_notifier.log import file_logger
from quota_notifier.orm import DBConnection
from quota_notifier.settings import ApplicationSettings


class Defaults(TestCase):
    """Test default settings"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set application settings to default values"""

        ApplicationSettings.reset_defaults()

    def test_blacklisted_root_user(self) -> None:
        """Test root is in blacklisted users"""

        self.assertEqual({0, }, ApplicationSettings.get('uid_blacklist'))

    def test_blacklisted_root_group(self) -> None:
        """Test root is in blacklisted groups"""

        self.assertEqual({0, }, ApplicationSettings.get('gid_blacklist'))


class ResetDefaults(TestCase):
    """Test the overwriting of settings via the ``reset_defaults`` method"""

    def test_blacklist_is_reset(self) -> None:
        """Test settings values are overwritten/reset by the ``reset_defaults`` method"""

        ApplicationSettings.set(uid_blacklist=[1])
        ApplicationSettings.reset_defaults()
        self.assertEqual({0, }, ApplicationSettings.get('uid_blacklist'))

    def test_database_connection_is_reconfigured(self) -> None:
        """Test the database connection is reconfigured after resetting defaults"""

        # Change the DB URL and then reset it to the default
        with NamedTemporaryFile() as temp_file:
            tem_db_path = f'sqlite:///{Path(temp_file.name).resolve()}'
            ApplicationSettings.set(db_url=tem_db_path)

            ApplicationSettings.reset_defaults()
            self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)

    def test_logging_is_reconfigured(self) -> None:
        """Test logging is reconfigured to ignore log files"""

        with NamedTemporaryFile(suffix='.log') as temp_log_file:
            ApplicationSettings.set(log_path=temp_log_file.name)
            ApplicationSettings.reset_defaults()

            self.assertIsNone(ApplicationSettings.get('log_path'))
            for handler in file_logger.handlers:
                self.assertGreaterEqual(1000, handler.level)


class ConfigureFromFile(TestCase):
    """Test the modification of settings via the ``configure_from_file`` method"""

    def test_setting_are_overwritten(self) -> None:
        """Test settings are overwritten with values from the file"""

        settings = dict(uid_blacklist=[3, 4, [5, 100]])

        with NamedTemporaryFile() as temp_file:
            path_obj = Path(temp_file.name)
            with path_obj.open('w') as io:
                json.dump(settings, io)

            ApplicationSettings.set_from_file(path_obj)
            self.assertEqual({3, 4, (5, 100)}, ApplicationSettings.get('uid_blacklist'))

    def test_invalid_file(self) -> None:
        """Test a ``ValidationError`` is raised for an invalid settings file"""

        settings = dict(extra_key=['bad_value'])

        with NamedTemporaryFile() as temp_file:
            path_obj = Path(temp_file.name)
            with path_obj.open('w') as io:
                json.dump(settings, io)

            with self.assertRaisesRegex(ValidationError, 'extra fields not permitted'):
                ApplicationSettings.set_from_file(path_obj)


class Set(TestCase):
    """Test application settings can be manipulated via the ``set`` method"""

    def test_setting_is_updated(self) -> None:
        """Test settings are updated by the setter"""

        new_setting_value = 'test@some_domain.com'
        ApplicationSettings.set(email_from=new_setting_value)
        self.assertEqual(new_setting_value, ApplicationSettings.get('email_from'))

    def test_error_invalid_setting(self) -> None:
        """Test a ``ValueError`` is raised for an invalid setting name"""

        with self.assertRaises(ValueError):
            ApplicationSettings.set(fakesetting=1)

    def test_db_is_configured(self):
        """Test the database connection is reconfigured after updating settings"""

        # Change the DB URL and then reset it to the default
        with NamedTemporaryFile() as temp_file:
            tem_db_path = f'sqlite:///{Path(temp_file.name).resolve()}'
            ApplicationSettings.set(db_url=tem_db_path)
            self.assertEqual(tem_db_path, DBConnection.url)


class LoggingConfiguration(TestCase):
    """Test the configuration of application logging"""

    def setUp(self) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    @classmethod
    def tearDownClass(cls) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    def test_no_logger_by_default(self) -> None:
        """Test a file logger is not configured by default"""

        self.assertIsNone(ApplicationSettings.get('log_path'))
        for handler in file_logger.handlers:
            self.assertGreaterEqual(1000, handler.level)

    def test_logging_level(self):
        """Test the logging level is updated to reflect application settings"""

        for level in ('DEBUG', 'INFO', 'WARNING', 'ERROR'):
            with NamedTemporaryFile(suffix='.log') as temp_log_file:
                ApplicationSettings.set(log_path=temp_log_file.name, log_level=level)

                for handler in file_logger.handlers:
                    handler_level_str = logging.getLevelName(handler.level)
                    self.assertEqual(level, handler_level_str)


class DatabaseConfiguration(TestCase):
    """Test configuration of the application database"""

    def setUp(self) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    @classmethod
    def tearDownClass(cls) -> None:
        """Reset application settings to defaults"""

        ApplicationSettings.reset_defaults()

    def test_db_in_memory(self) -> None:
        """Test debug mode forces an in-memory database"""

        ApplicationSettings.set(db_url='sqlite:///:memory:')
        self.assertEqual('sqlite:///:memory:', DBConnection.url)

    def test_db_matches_default_settings(self) -> None:
        """Test debug mode forces an in-memory database"""

        self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)
