"""Tests for the ``AbstractFileSystemUsage`` class"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from unittest import TestCase

from quota_notifier.disk_utils import AbstractQuota
from quota_notifier.shell import User


class Initialization(TestCase):

    def test_error_on_empty_name(self) -> None:
        """Test for a ``ValueError`` when the quota name is empty"""

        with self.assertRaises(ValueError):
            AbstractQuota(name='', user=User('root'), path=Path('/'), size_used=10, size_limit=100)

        with self.assertRaises(ValueError):
            AbstractQuota(name=' ', user=User('root'), path=Path('/'), size_used=10, size_limit=100)


class DummyQuotaObj(AbstractQuota):
    """Subclass of an abstract parent to use in testing"""

    @classmethod
    def get_quota(cls, name: str, path: Path, user: User) -> Optional[DummyQuotaObj]:
        """Return an instance of the parent class"""

        return DummyQuotaObj(name=name, user=user, path=Path('/'), size_used=10, size_limit=100)


class BytesToString(TestCase):
    """Test the conversion of bytes into human-readable strings"""

    def test_zero_bytes(self) -> None:
        """Test the conversion of zero bytes"""

        self.assertEqual('0.0 B', AbstractQuota.bytes_to_str(0))

    def test_integer_conversion(self) -> None:
        """Test the conversion from bytes to known values that do not have trailing decimals"""

        inputs = (1, 2 ** 10, 2 ** 20, 2 ** 30, 2 ** 40, 2 ** 50, 2 ** 60, 2 ** 70, 2 ** 80)
        outputs = ('1.0 B', '1.0 KB', '1.0 MB', '1.0 GB', '1.0 TB', '1.0 PB', '1.0 EB', '1.0 ZB', '1.0 YB')

        for inp, oup in zip(inputs, outputs):
            self.assertEqual(oup, AbstractQuota.bytes_to_str(inp))

    def test_non_integer_values(self) -> None:
        """Test the conversion from bytes to known values with trailing decimals"""

        inputs = map(int, (5.0E5, 5.0E7, 5.0E9, 5.0E12))
        outputs = ('488.28 KB', '47.68 MB', '4.66 GB', '4.55 TB')

        for inp, oup in zip(inputs, outputs):
            self.assertEqual(oup, AbstractQuota.bytes_to_str(inp))


class StringRepresentation(TestCase):
    """Test the representation of quota objects as a string"""

    def test_string_matches_expectation(self) -> None:
        """Test string casting matches an expected string"""

        quota = DummyQuotaObj.get_quota('dummy_system', Path('/'), User('root'))

        # Manually define the expected string using the same values used when defining DummyQuotaObj
        self.assertEqual("dummy_system: 10.0 B / 100.0 B (10%)", str(quota))
