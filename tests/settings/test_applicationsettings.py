"""Tests for the ``ApplicationSettings`` class"""

from unittest import TestCase

from app.settings import ApplicationSettings


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
