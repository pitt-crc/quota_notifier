"""Tests for the ``GenericQuota`` class."""

from pathlib import Path
from unittest import TestCase

from quota_notifier.disk_utils import GenericQuota
from quota_notifier.shell import User


class GetQuota(TestCase):
    """Test the ``get_quota`` factory method"""

    def test_none_on_missing_path(self) -> None:
        """Test ``None`` is returned when the file path does not exist"""

        quota = GenericQuota.get_quota(name='name', user=User('root'), path=Path('/fake/path'))
        self.assertIsNone(quota)

    def test_quota_matches_user(self) -> None:
        """Test the returned quota object matches the requested user"""

        user = User('root')
        quota = GenericQuota.get_quota(name='name', user=user, path=Path('/'))
        self.assertEqual(user, quota.user)

    def test_quota_matches_path(self) -> None:
        """Test the returned quota object matches the requested path"""

        path = Path('/')
        quota = GenericQuota.get_quota(name='name', user=User('root'), path=path)
        self.assertEqual(path, quota.path)
