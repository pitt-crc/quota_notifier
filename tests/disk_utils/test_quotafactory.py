"""Tests for the ``QuotaFactory`` class"""
from pathlib import Path
from unittest import TestCase

from quota_notifier.disk_utils import GenericQuota, QuotaFactory
from quota_notifier.shell import User


class ReturnedQuotaType(TestCase):
    """Test returned quotas match the expected type"""

    def test_error_invalid_type(self) -> None:
        """Test a ``ValueError`` is raised for invalid quota types"""

        with self.assertRaises(ValueError):
            QuotaFactory(quota_type='fake_type', name='test_quota', path=Path('/'), user=User('root'))

    def test_type_matches_argument(self) -> None:
        """Test the returned type matches the ``quota_type`` argument"""

        quota = QuotaFactory(quota_type='generic', name='test_quota', path=Path('/'), user=User('root'))
        self.assertIsInstance(quota, GenericQuota)

    def test_quota_matches_user(self) -> None:
        """Test the returned quota object matches the requested user"""

        user = User('root')
        quota = QuotaFactory(quota_type='generic', name='name', user=user, path=Path('/'))
        self.assertEqual(user, quota.user)

    def test_quota_matches_path(self) -> None:
        """Test the returned quota object matches the requested path"""

        path = Path('/')
        quota = QuotaFactory(quota_type='generic', name='name', user=User('root'), path=path)
        self.assertEqual(path, quota.path)
