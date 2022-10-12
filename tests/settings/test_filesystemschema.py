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
        """Test a ``ValueError`` is raised for non-existent paths"""

        with self.assertRaises(ValueError):
            FileSystemSchema.validate_path(Path('/fake/path'))

    def test_valid_path(self) -> None:
        """Test the path value is returned for a valid path"""

        valid_path = Path('/')
        returned_path = FileSystemSchema.validate_path(valid_path)
        self.assertEqual(valid_path, returned_path)


class TypeValidation(TestCase):
    """Test validation of the ``type`` filed"""

    def test_valid_types_pass(self) -> None:
        """Test valid types do not raise errors"""

        for fs_type in QuotaFactory.QuotaType:
            fs_type_string = fs_type.name
            self.assertEqual(fs_type, FileSystemSchema.validate_type(fs_type_string))

    def test_invalid_type_error(self) -> None:
        """Test a ``ValueError`` is raised for invalid types"""

        with self.assertRaises(ValueError):
            FileSystemSchema.validate_type('fake_type')
