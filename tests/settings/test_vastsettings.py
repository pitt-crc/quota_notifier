"""Tests for validation of VAST API settings in the ``SettingsSchema`` class"""

import secrets
from unittest import TestCase

from quota_notifier.settings import SettingsSchema

TEST_TOKEN = secrets.token_hex(8)
TEST_PASSWORD = secrets.token_hex(8)

IHOME_SYSTEM = {'name': 'ihome', 'path': '/', 'type': 'ihome', 'thresholds': [50]}
GENERIC_SYSTEM = {'name': 'generic', 'path': '/', 'type': 'generic', 'thresholds': [50]}


class VastSettingsValidation(TestCase):
    """Test VAST settings are required for ihome file systems"""

    @staticmethod
    def test_not_required_without_ihome() -> None:
        """Test VAST settings are optional when no ihome file system is configured"""

        SettingsSchema.model_validate({'file_systems': [GENERIC_SYSTEM]})

    def test_missing_host(self) -> None:
        """Test an error is raised when the VAST host is missing"""

        with self.assertRaisesRegex(Exception, 'vast_host'):
            SettingsSchema.model_validate({'file_systems': [IHOME_SYSTEM], 'vast_token': TEST_TOKEN})

    def test_missing_credentials(self) -> None:
        """Test an error is raised when no VAST credentials are given"""

        with self.assertRaisesRegex(Exception, 'vast_token'):
            SettingsSchema.model_validate({'file_systems': [IHOME_SYSTEM], 'vast_host': 'vms'})

        with self.assertRaisesRegex(Exception, 'vast_token'):
            SettingsSchema.model_validate({'file_systems': [IHOME_SYSTEM], 'vast_host': 'vms', 'vast_user': 'u'})

    def test_both_credentials(self) -> None:
        """Test an error is raised when both a token and username/password are given"""

        with self.assertRaisesRegex(Exception, 'vast_token'):
            SettingsSchema.model_validate({
                'file_systems': [IHOME_SYSTEM], 'vast_host': 'vms',
                'vast_token': TEST_TOKEN, 'vast_user': 'u', 'vast_password': TEST_PASSWORD})

    @staticmethod
    def test_valid_credentials() -> None:
        """Test either a token or a username/password passes validation"""

        SettingsSchema.model_validate({'file_systems': [IHOME_SYSTEM], 'vast_host': 'vms', 'vast_token': TEST_TOKEN})
        SettingsSchema.model_validate({
            'file_systems': [IHOME_SYSTEM], 'vast_host': 'vms', 'vast_user': 'u', 'vast_password': TEST_PASSWORD})

    def test_secrets_are_masked(self) -> None:
        """Test credentials are not exposed in the settings string representation"""

        settings = SettingsSchema.model_validate({
            'file_systems': [IHOME_SYSTEM], 'vast_host': 'vms', 'vast_user': 'u', 'vast_password': TEST_PASSWORD})
        self.assertNotIn(TEST_PASSWORD, str(settings))
