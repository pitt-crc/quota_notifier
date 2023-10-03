"""Tests for the ``ApplicationSettings`` class"""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

from quota_notifier.settings import ApplicationSettings
from tests.base import DefaultSetupTeardown


class Defaults(DefaultSetupTeardown, TestCase):
    """Test default settings"""

    def test_blacklisted_root_user(self) -> None:
        """Test root is in blacklisted users"""

        self.assertEqual({0, }, ApplicationSettings.get('uid_blacklist'))

    def test_blacklisted_root_group(self) -> None:
        """Test root is in blacklisted groups"""

        self.assertEqual({0, }, ApplicationSettings.get('gid_blacklist'))


class ResetDefaults(DefaultSetupTeardown, TestCase):
    """Test the overwriting of settings via the ``reset_defaults`` method"""

    def test_blacklist_is_reset(self) -> None:
        """Test settings values are overwritten/reset by the ``reset_defaults`` method"""

        ApplicationSettings.set(uid_blacklist=[1])
        ApplicationSettings.reset_defaults()
        self.assertEqual({0, }, ApplicationSettings.get('uid_blacklist'))


class ConfigureFromFile(DefaultSetupTeardown, TestCase):
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

            with self.assertRaisesRegex(Exception, 'Extra inputs are not permitted'):
                ApplicationSettings.set_from_file(path_obj)


class Set(DefaultSetupTeardown, TestCase):
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
