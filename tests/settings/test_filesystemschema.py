"""Tests for the ``FileSystemSchema`` class"""

from pathlib import Path
from unittest import TestCase

from app.disk_utils import QuotaFactory
from app.settings import FileSystemSchema


class PathValidation(TestCase):
    """Test validation of the ``path`` field"""

    def test_path_exists(self) -> None:
        """Test existing file paths do not raise errors"""

        test_path = Path('/')
        self.assertEqual(test_path, FileSystemSchema.validate_path(test_path))

    def test_nonexistent_path(self) -> None:
        """Test a ``ValueError`` is raised for non-existant paths"""

        with self.assertRaises(ValueError):
            FileSystemSchema.validate_path(Path('/fake/path'))


class TypeValidation(TestCase):
    """Test validation of the ``type`` filed"""

    def test_valid_types_pass(self) -> None:
        """Test valid types do not raise errors"""

        for fs_type in QuotaFactory.quota_types:
            self.assertEqual(fs_type, FileSystemSchema.validate_type(fs_type))

    def test_invalid_type_error(self) -> None:
        """Test a ``ValueError`` is raised for invalid types"""

        with self.assertRaises(ValueError):
            FileSystemSchema.validate_type('fake_type')
