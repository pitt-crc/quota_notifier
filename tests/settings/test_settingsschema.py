"""Tests for the ``SettingsSchema`` class"""

from pathlib import Path
from unittest import TestCase

import app
from app.settings import SettingsSchema


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
