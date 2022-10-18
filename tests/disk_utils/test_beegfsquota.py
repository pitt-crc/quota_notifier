"""Tests for the ``BeeGFSQuota`` class."""

from pathlib import Path
from unittest import TestCase

from quota_notifier.disk_utils import BeeGFSQuota
from quota_notifier.shell import User


class GetQuota(TestCase):
    """Test the ``get_quota`` factory method"""

    def test_error_on_missing_path(self) -> None:
        """Test for a ``FileNotFoundError`` when the file path does not exist"""

        with self.assertRaises(FileNotFoundError):
            BeeGFSQuota.get_quota(name='name', user=User('root'), path=Path('/fake/path'))
