"""Tests for the ``SettingsSchema`` class"""

import tempfile
from pathlib import Path
from unittest import TestCase

from quota_notifier.settings import FileSystemSchema, SettingsSchema


class VerbosityValidation(TestCase):
    """Test validation for the ``verbosity`` field"""

    def test_valid_integers(self) -> None:
        """Test integers 0 through 2 are valid options"""

        for value in range(3):
            self.assertEqual(value, SettingsSchema(verbosity=value).verbosity)

    def test_float_error(self) -> None:
        """Test a ``ValueError`` is raised for float values"""

        for value in (1.1, 3.5, 10.7):
            with self.assertRaises(ValueError):
                SettingsSchema(verbosity=value)

    def test_negative_error(self) -> None:
        """Test a ``ValueError`` is raised for negative integers"""

        for value in (-1, -5, -100):
            with self.assertRaises(ValueError):
                SettingsSchema(verbosity=value)

    def test_large_integer_error(self) -> None:
        """Test a ``ValueError`` is raised for integers over 2"""

        for value in (3, 10, 100):
            with self.assertRaises(ValueError):
                SettingsSchema(verbosity=value)


class FileSystemValidation(TestCase):
    """Test validation for the ``file_systems`` field"""

    def test_error_on_duplicate_path(self) -> None:
        """Test a ``ValueError`` is raised when file systems have duplicate paths"""

        # Test objects have different names but the same path
        system_1 = FileSystemSchema(name='name1', path=Path('/'), type='generic')
        system_2 = FileSystemSchema(name='name2', path=system_1.path, type='generic')

        with self.assertRaisesRegex(ValueError, 'File systems do not have unique paths'):
            SettingsSchema.validate_unique_file_systems([system_1, system_2])

    def test_error_on_duplicate_name(self) -> None:
        """Test a ``ValueError`` is raised when file systems have duplicate names"""

        with tempfile.TemporaryDirectory() as tempdir1, tempfile.TemporaryDirectory() as tempdir2:
            # Test objects have different names but the same path
            system_1 = FileSystemSchema(name='name', path=Path(tempdir1), type='generic')
            system_2 = FileSystemSchema(name=system_1.name, path=Path(tempdir2), type='generic')

            with self.assertRaisesRegex(ValueError, 'File systems do not have unique names'):
                SettingsSchema.validate_unique_file_systems([system_1, system_2])

    def test_valid_values_returned(self) -> None:
        """Test valid values are returned by the validator"""

        valid_input = [FileSystemSchema(name='name1', path=Path('/'), type='generic')]
        returned_value = SettingsSchema.validate_unique_file_systems(valid_input)
        self.assertEqual(valid_input, returned_value)


class DefaultDBUrl(TestCase):
    """Tests for the default database path"""

    def test_is_sqlite(self) -> None:
        """Test the default path is structured as a SQLite database"""

        self.assertTrue(SettingsSchema().db_url.startswith('sqlite:///'))

    def test_in_app_dir(self) -> None:
        """Test the default path is located in the current working directory"""

        app_path = Path(quota_notifier.__file__).resolve()
        db_path = Path(SettingsSchema().db_url.replace('sqlite:///', ''))
        self.assertTrue(db_path.is_absolute(), msg='Database path is not absolute')
        self.assertEqual(app_path.parent, db_path.parent)
