"""Tests for the ``FileSystemSchema`` class"""

import string
from pathlib import Path
from unittest import TestCase

from pydantic import ValidationError

from quota_notifier.disk_utils import QuotaFactory
from quota_notifier.settings import FileSystemSchema


class NameValidation(TestCase):
    """Test validation of the file system ``name`` field"""

    def test_blank_name(self) -> None:
        """Test a ``ValueError`` is raised for empty/blank names"""

        with self.assertRaisesRegex(ValueError, 'File system name cannot be blank'):
            FileSystemSchema.validate_name('')

        for char in string.whitespace:
            with self.assertRaisesRegex(ValueError, 'File system name cannot be blank'):
                FileSystemSchema.validate_name(char)


class PathValidation(TestCase):
    """Test validation of the ``path`` field"""

    def test_path_exists(self) -> None:
        """Test existing file paths do not raise errors"""

        test_path = Path('/')
        self.assertEqual(test_path, FileSystemSchema.validate_path(test_path))

    def test_nonexistent_path(self) -> None:
        """Test a ``ValueError`` is raised for non-existent paths"""

        with self.assertRaisesRegex(ValueError, 'File system does not exist'):
            FileSystemSchema.validate_path(Path('/fake/path'))

    def test_valid_path(self) -> None:
        """Test the path value is returned for a valid path"""

        valid_path = Path('/')
        returned_path = FileSystemSchema.validate_path(valid_path)
        self.assertEqual(valid_path, returned_path)


class TypeValidation(TestCase):
    """Test validation of the ``type`` filed"""

    @staticmethod
    def test_valid_types_pass() -> None:
        """Test valid types do not raise errors"""

        for fs_type in QuotaFactory.QuotaType:
            FileSystemSchema(name='name', type=fs_type.name, path='/')

    def test_invalid_type_error(self) -> None:
        """Test a ``ValueError`` is raised for invalid types"""

        with self.assertRaisesRegex(ValidationError, 'type\n  unexpected value;'):
            FileSystemSchema(type='fake_type')
