"""Tests for the ``Parser`` class."""

from pathlib import Path
from unittest import TestCase

from quota_notifier.cli import DEFAULT_SETTINGS, Parser


class ParserHelpData(TestCase):
    """Test the parser is configured with help data"""

    def test_custom_prog_name(self) -> None:
        """Test the application name is set to ``notifier``"""

        self.assertEqual('notifier', Parser().prog)

    def test_has_description(self) -> None:
        """Test the application description is not empty"""

        self.assertTrue(Parser().description)


class SettingsOption(TestCase):
    """Test parsing of the ``--settings`` option"""

    def test_default_config_path(self) -> None:
        """Test the default settings path matches globally defined values"""

        args = Parser().parse_args([])
        self.assertEqual(DEFAULT_SETTINGS, args.settings)

    def test_stored_as_path(self) -> None:
        """Test the parsed value is stored as a ``Path`` object"""

        test_path_str = '/my/test/path'
        args = Parser().parse_args(['-s', test_path_str])
        self.assertEqual(Path(test_path_str), args.settings)


class CheckOption(TestCase):
    """Test parsing of the ``--check`` option"""

    def test_defaults_to_false(self) -> None:
        """Test the ``check`` flag defaults to ``False``"""

        args = Parser().parse_args([])
        self.assertFalse(args.check)

    def test_stores_as_true(self) -> None:
        """Test the ``check`` flag defaults to ``False``"""

        args = Parser().parse_args(['--check'])
        self.assertTrue(args.check)
