"""Tests for the ``FileSystemSchema`` class"""

import string
from pathlib import Path
from unittest import TestCase

from pydantic import ValidationError

from quota_notifier.disk_utils import QuotaFactory
from quota_notifier.settings import FileSystemSchema
from tests.base import DefaultSetupTeardown


class NameValidation(DefaultSetupTeardown, TestCase):
    """Test validation of the file system ``name`` field"""

    def test_blank_name_error(self) -> None:
        """Test a ``ValueError`` is raised for empty/blank names"""

        with self.assertRaisesRegex(ValueError, 'File system name cannot be blank'):
            FileSystemSchema(name='')

        for char in string.whitespace:
            with self.assertRaisesRegex(ValueError, 'File system name cannot be blank'):
                FileSystemSchema(name=char)

    def test_whitespace_is_stripped(self) -> None:
        """Test leading/trailing whitespace is stripped from filesystem names"""

        validated_name = FileSystemSchema.validate_name(' abc ')
        self.assertEqual('abc', validated_name)


class PathValidation(DefaultSetupTeardown, TestCase):
    """Test validation of the ``path`` field"""

    def test_existing_path_validates(self) -> None:
        """Test existing file paths do not raise errors"""

        valid_path = Path('/')
        returned_path = FileSystemSchema.validate_path(valid_path)
        self.assertEqual(valid_path, returned_path)

    def test_nonexistent_path(self) -> None:
        """Test a ``ValueError`` is raised for non-existent paths"""

        with self.assertRaisesRegex(ValueError, 'File system path does not exist'):
            FileSystemSchema.validate_path(Path('/fake/path'))


class TypeValidation(DefaultSetupTeardown, TestCase):
    """Test validation of the ``type`` field"""

    @staticmethod
    def test_valid_types_pass() -> None:
        """Test valid types do not raise errors"""

        for fs_type in QuotaFactory.QuotaType:
            FileSystemSchema(name='name', type=fs_type.name, path='/', thresholds=[50])

    def test_invalid_type_error(self) -> None:
        """Test a ``ValueError`` is raised for invalid types"""

        with self.assertRaisesRegex(ValidationError, 'type\n  unexpected value;'):
            FileSystemSchema(type='fake_type')


class ThresholdValidation(DefaultSetupTeardown, TestCase):
    """Test validation of the ``threshold`` field"""

    def test_intermediate_values_pass(self) -> None:
        """Test values greater than 0 and less than 100 pass validation"""

        test_thresholds = [1, 25, 50, 75, 99]
        validated_value = FileSystemSchema.validate_thresholds(test_thresholds)
        self.assertCountEqual(test_thresholds, validated_value)

    def test_empty_list_fails(self) -> None:
        """Test an empty collection of thresholds fails validation"""

        with self.assertRaisesRegex(ValidationError, 'At least one threshold must be specified'):
            FileSystemSchema(thresholds=[])

    def test_zero_percent(self) -> None:
        """Test the value ``0`` fails validation"""

        with self.assertRaisesRegex(ValidationError, 'must be greater than 0 and less than 100'):
            FileSystemSchema(thresholds=[0, 50])

    def test_100_percent(self) -> None:
        """Test the value ``100`` fails validation"""

        with self.assertRaisesRegex(ValidationError, 'must be greater than 0 and less than 100'):
            FileSystemSchema(thresholds=[50, 100])

    def test_negative_percent(self) -> None:
        """Test negative values fail validation"""

        with self.assertRaisesRegex(ValidationError, 'must be greater than 0 and less than 100'):
            FileSystemSchema(thresholds=[-1, 50])

    def test_over_100_percent(self) -> None:
        """Test values over ``100`` fail validation"""

        with self.assertRaisesRegex(ValidationError, 'must be greater than 0 and less than 100'):
            FileSystemSchema(thresholds=[50, 101])
