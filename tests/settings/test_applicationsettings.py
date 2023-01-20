"""Tests for the ``ApplicationSettings`` class"""

import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from pydantic import ValidationError

from quota_notifier.orm import DBConnection
from quota_notifier.settings import ApplicationSettings


class Defaults(TestCase):
    """Test default settings"""

    @classmethod
    def setUpClass(cls) -> None:
        ApplicationSettings.reset_defaults()

    def test_blacklisted_users(self) -> None:
        """Test root is in blacklisted users"""

        self.assertEqual({0,}, ApplicationSettings.get('uid_blacklist'))

    def test_blacklisted_groups(self) -> None:
        """Test root is in blacklisted groups"""

        self.assertEqual({0,}, ApplicationSettings.get('gid_blacklist'))


class ResetDefaults(TestCase):
    """Test the overwriting of settings via the ``reset_defaults`` method"""

    def test_blacklist_is_reset(self) -> None:
        """Test settings values are overwritten/reset by the ``reset_defaults`` method"""

        ApplicationSettings.set(uid_blacklist=['fake_username'])
        ApplicationSettings.reset_defaults()
        self.assertEqual({0,}, ApplicationSettings.get('uid_blacklist'))

    def test_database_connection_is_reconfigured(self) -> None:
        """Test the database connection is reconfigured after resetting defaults"""

        # Change the DB URL and then reset it to the default
        with NamedTemporaryFile() as temp_file:
            tem_db_path = f'sqlite:///{Path(temp_file.name).resolve()}'
            ApplicationSettings.set(db_url=tem_db_path)

            ApplicationSettings.reset_defaults()
            self.assertEqual(ApplicationSettings.get('db_url'), DBConnection.url)


class ConfigureFromFile(TestCase):
    """Test the modification of settings via the ``configure_from_file`` method"""

    def test_setting_are_overwritten(self) -> None:
        """Test settings are overwritten with values from the file"""

        settings = dict(uid_blacklist=[3, 4, 5])

        with NamedTemporaryFile() as temp_file:
            path_obj = Path(temp_file.name)
            with path_obj.open('w') as io:
                json.dump(settings, io)

            ApplicationSettings.set_from_file(path_obj)
            self.assertEqual({3, 4, 5}, ApplicationSettings.get('uid_blacklist'))

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

    def test_logging_format_set(self):
        """Test the logging format is configured"""

        log_format = logging.getLogger().handlers[0].formatter._fmt
        self.assertEqual('%(levelname)8s - %(message)s', log_format)

    def test_verbose_level_zero(self):
        """Test setting ``verbose=0`` blocks all logging"""

        ApplicationSettings.set(verbosity=0)
        self.assertEqual(100, logging.getLogger().level)

    def test_verbose_level_one(self):
        """Test setting ``verbose=1`` sets the logging level to ``WARNING``"""

        ApplicationSettings.set(verbosity=1)
        self.assertEqual(logging.WARNING, logging.getLogger().level)

    def test_verbose_level_two(self):
        """Test setting ``verbose=2`` sets the logging level to ``INFO``"""

        ApplicationSettings.set(verbosity=2)
        self.assertEqual(logging.INFO, logging.getLogger().level)

    def test_verbose_level_three(self):
        """Test setting ``verbose=3`` sets the logging level to ``DEBUG``"""

        ApplicationSettings.set(verbosity=3)
        self.assertEqual(logging.DEBUG, logging.getLogger().level)

    def test_verbose_level_100(self):
        """Test setting ``verbose=100`` sets the logging level to ``DEBUG``"""

        ApplicationSettings.set(verbosity=100)
        self.assertEqual(logging.DEBUG, logging.getLogger().level)


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
