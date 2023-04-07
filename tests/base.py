"""Custom parent classes and utilities for testing."""

from quota_notifier.settings import ApplicationSettings


class CleanSettingsMixin:
    """Mixin for resting application settings before and after every test"""

    def setUp(self) -> None:
        """Reset application settings"""

        ApplicationSettings.reset_defaults()

    def tearDown(self) -> None:
        """Reset application settings"""

        ApplicationSettings.reset_defaults()
