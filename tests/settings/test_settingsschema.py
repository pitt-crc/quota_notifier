"""Tests for the ``SettingsSchema`` class"""

import tempfile
from pathlib import Path
from unittest import TestCase

from quota_notifier.settings import FileSystemSchema, SettingsSchema
from tests.base import DefaultSetupTeardown


class BlacklistValidation(DefaultSetupTeardown, TestCase):
    """Test validation for the ``uid_blacklist`` and ``gid_blacklist`` fields"""

    def test_error_on_id_range_len_1(self) -> None:
        """Test a ``ValueError`` is raised for UID and GID ranges with 1 element"""

        with self.assertRaisesRegex(ValueError, 'actual_length=1; expected_length=2'):
            SettingsSchema(uid_blacklist=[[1], ])

        with self.assertRaisesRegex(ValueError, 'actual_length=1; expected_length=2'):
            SettingsSchema(gid_blacklist=[[1], ])

    def test_error_on_id_range_len_3(self) -> None:
        """Test a ``ValueError`` is raised for UID and GID ranges with 3 elements"""

        with self.assertRaisesRegex(ValueError, 'actual_length=3; expected_length=2'):
            SettingsSchema(uid_blacklist=[[1, 2, 3], ])

        with self.assertRaisesRegex(ValueError, 'actual_length=3; expected_length=2'):
            SettingsSchema(gid_blacklist=[[1, 2, 3], ])

    def test_error_on_account_names(self) -> None:
        """Test a useful error message is raised when users provide account names instead of IDs"""

        with self.assertRaisesRegex(ValueError, 'value is not a valid integer'):
            SettingsSchema(uid_blacklist=['root', ])

        with self.assertRaisesRegex(ValueError, 'value is not a valid integer'):
            SettingsSchema(gid_blacklist=['root', ])


class FileSystemValidation(DefaultSetupTeardown, TestCase):
    """Test validation for the ``file_systems`` field"""

    def test_error_on_duplicate_path(self) -> None:
        """Test a ``ValueError`` is raised when file systems have duplicate paths"""

        # Test objects have different names but the same path
        system_1 = FileSystemSchema(name='name1', path=Path('/'), type='generic', thresholds=[50])
        system_2 = FileSystemSchema(name='name2', path=system_1.path, type='generic', thresholds=[50])

        with self.assertRaisesRegex(ValueError, 'File systems do not have unique paths'):
            SettingsSchema.validate_unique_file_systems([system_1, system_2])

    def test_error_on_duplicate_name(self) -> None:
        """Test a ``ValueError`` is raised when file systems have duplicate names"""

        with tempfile.TemporaryDirectory() as tempdir1, tempfile.TemporaryDirectory() as tempdir2:
            # Test objects have different names but the same path
            system_1 = FileSystemSchema(name='name', path=Path(tempdir1), type='generic', thresholds=[50])
            system_2 = FileSystemSchema(name=system_1.name, path=Path(tempdir2), type='generic', thresholds=[50])

            with self.assertRaisesRegex(ValueError, 'File systems do not have unique names'):
                SettingsSchema.validate_unique_file_systems([system_1, system_2])

    def test_valid_values_returned(self) -> None:
        """Test valid values are returned by the validator"""

        valid_input = [FileSystemSchema(name='name1', path=Path('/'), type='generic', thresholds=[50])]
        returned_value = SettingsSchema.validate_unique_file_systems(valid_input)
        self.assertEqual(valid_input, returned_value)


class DefaultDBUrl(DefaultSetupTeardown, TestCase):
    """Tests for the default database path"""

    def test_is_sqlite(self) -> None:
        """Test the default path is structured as a SQLite database"""

        self.assertTrue(SettingsSchema().db_url.startswith('sqlite:///'))

    def test_in_cwd(self) -> None:
        """Test the default path is located in the current working directory"""

        db_path = Path(SettingsSchema().db_url.replace('sqlite:///', ''))
        self.assertTrue(db_path.is_absolute(), msg='Database path is not absolute')
        self.assertEqual(Path.cwd(), db_path.parent)
