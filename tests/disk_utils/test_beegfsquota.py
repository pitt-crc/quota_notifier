"""Tests for the ``BeeGFSQuota`` class."""

from pathlib import Path
from unittest import TestCase

from quota_notifier.disk_utils import BeeGFSQuota
from quota_notifier.shell import User


class GetQuota(TestCase):
    """Test the ``get_quota`` factory method"""

    def test_none_on_missing_path(self) -> None:
        """Test ``None`` is returned when the file path does not exist"""

        quota = BeeGFSQuota.get_quota(name='name', user=User('root'), path=Path('/fake/path'))
        self.assertIsNone(quota)