"""Tests for the ``ApplicationSettings`` class"""

from unittest import TestCase

from app.settings import ApplicationSettings


class Configure(TestCase):
    """Test the modification of settings via the ``configure`` method"""

    def test_setting_are_modified(self) -> None:
        # Check settings are overwritten
        ApplicationSettings.configure(blacklist=['fakeusername'])
        self.assertListEqual(['fakeusername'], ApplicationSettings.get('blacklist'))

        # Test settings are restored
        ApplicationSettings.configure()
        self.assertFalse(ApplicationSettings.get('blacklist'))
