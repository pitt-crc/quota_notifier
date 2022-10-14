"""Tests for the ``ApplicationSettings`` class"""

from unittest import TestCase

from quota_notifier.settings import ApplicationSettings


class Configure(TestCase):
    """Test the modification of settings via the ``configure`` method"""

    def test_setting_are_modified(self) -> None:
        """Test settings values are overwritten/reset by the ``configure`` method"""

        # Check settings are overwritten
        ApplicationSettings.configure(blacklist=['fake_username'])
        self.assertListEqual(['fake_username'], ApplicationSettings.get('blacklist'))

        # Test settings are restored
        ApplicationSettings.configure()
        self.assertFalse(ApplicationSettings.get('blacklist'))


class Setter(TestCase):
    """Test application settings can be manipulated via the setter method"""

    def test_settings_is_updated(self) -> None:
        """Test settings are updated by the setter"""

        new_setting_value = 'test@some_domain.com'
        ApplicationSettings.set(email_from=new_setting_value)
        self.assertEqual(new_setting_value, ApplicationSettings.get('email_from'))

    def test_error_invalid_settings(self) -> None:
        """Test a ``ValueError`` is raised for an invalid settings name"""

        with self.assertRaises(ValueError):
            ApplicationSettings.set(fakesetting=1)
