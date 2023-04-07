"""Custom parent classes and utilities for testing."""

from quota_notifier.settings import ApplicationSettings


class DefaultSetupTeardown:
    """Defines setup/tear down steps for resting default settings before/after every test"""

    def setUp(self) -> None:
        """Reset application settings"""

        ApplicationSettings.reset_defaults()

    def tearDown(self) -> None:
        """Reset application settings"""

        ApplicationSettings.reset_defaults()
