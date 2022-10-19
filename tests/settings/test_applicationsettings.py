"""Tests for the ``ApplicationSettings`` class"""
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from pydantic import ValidationError

from quota_notifier.settings import ApplicationSettings


class Configure(TestCase):
    """Test the modification of settings via the ``configure`` method"""

    def test_setting_are_overwritten(self) -> None:
        """Test settings values are overwritten/reset by the ``configure`` method"""

        # Check settings are overwritten
        ApplicationSettings.configure(blacklist=['fake_username'])
        self.assertListEqual(['fake_username'], ApplicationSettings.get('blacklist'))

        # Test settings are restored
        ApplicationSettings.configure()
        self.assertFalse(ApplicationSettings.get('blacklist'))


class ConfigureFromFile(TestCase):
    """Test the modification of settings via the ``configure_from_file`` method"""

    def test_setting_are_overwritten(self) -> None:
        """Test settings are overwritten with values from the file"""

        settings = dict(blacklist=['fake_username'])

        with NamedTemporaryFile() as temp_file:
            path_obj = Path(temp_file.name)
            with path_obj.open('w') as io:
                json.dump(settings, io)

            ApplicationSettings.configure_from_file(path_obj)
            self.assertEqual({'fake_username'}, ApplicationSettings.get('blacklist'))

    def test_invalid_file(self) -> None:
        """Test a ``ValidationError`` is raised for an invalid settings file"""

        settings = dict(extra_key=['bad_value'])

        with NamedTemporaryFile() as temp_file:
            path_obj = Path(temp_file.name)
            with path_obj.open('w') as io:
                json.dump(settings, io)

            with self.assertRaisesRegex(ValidationError, 'extra fields not permitted'):
                ApplicationSettings.configure_from_file(path_obj)


class Setter(TestCase):
    """Test application settings can be manipulated via the setter method"""

    def test_setting_is_updated(self) -> None:
        """Test settings are updated by the setter"""

        new_setting_value = 'test@some_domain.com'
        ApplicationSettings.set(email_from=new_setting_value)
        self.assertEqual(new_setting_value, ApplicationSettings.get('email_from'))

    def test_error_invalid_setting(self) -> None:
        """Test a ``ValueError`` is raised for an invalid setting name"""

        with self.assertRaises(ValueError):
            ApplicationSettings.set(fakesetting=1)
