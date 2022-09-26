"""Tests for the ``SettingsSchema`` class"""

from pathlib import Path
from unittest import TestCase

import app
from app.settings import FileSystemSchema, SettingsSchema


class DefaultDBUrl(TestCase):
    """Tests for the default database path"""

    def test_is_sqlite(self) -> None:
        """Test the default path is structured as a SQLite database"""

        self.assertTrue(SettingsSchema().db_url.startswith('sqlite:///'))

    def test_in_app_dir(self) -> None:
        """Test the default path is located inside the package directory"""

        app_path = Path(app.__file__).resolve()
        db_path = Path(SettingsSchema().db_url.replace('sqlite:///', ''))
        self.assertTrue(db_path.is_absolute(), msg='Database path is not absolute')
        self.assertEqual(app_path.parent, db_path.parent)


class FileSystemValidation(TestCase):
    """Test validation for the ``file_systmes`` field"""

    def test_error_on_duplicate(self) -> None:
        """Test a ``ValueError`` is raised when passed duplicate file systems"""

        # Test objects have different names but the same path
        system_1 = FileSystemSchema(name='name1', path=Path('/'), type='generic')
        system_2 = FileSystemSchema(name='name2', path=system_1.path, type='generic')

        with self.assertRaises(ValueError):
            SettingsSchema.validate_file_systems([system_1, system_2])
