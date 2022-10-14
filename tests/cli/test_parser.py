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


class ValidateOption(TestCase):
    """Test parsing of the ``--validate`` option"""

    def test_defaults_to_false(self) -> None:
        """Test the ``validate`` flag defaults to ``False``"""

        args = Parser().parse_args([])
        self.assertFalse(args.validate)

    def test_stores_as_true(self) -> None:
        """Test the ``validate`` flag defaults to ``False``"""

        args = Parser().parse_args(['--validate'])
        self.assertTrue(args.validate)


class VerboseOption(TestCase):
    """Test parsing of the ``--verbose`` option"""

    def test_defaults_to_zero(self) -> None:
        """Test the ``verbose`` value is zero when not specified"""

        args = Parser().parse_args([])
        self.assertEqual(0, args.verbose)

    def test_defaults_to_one(self) -> None:
        """Test the ``verbose`` value is one when specified without arguments"""

        args = Parser().parse_args(['--verbose'])
        self.assertEqual(1, args.verbose)

    def test_accepts_custom_value(self) -> None:
        """Test custom arguments are stored in the returned arguemnts"""

        args = Parser().parse_args(['--verbose', '2'])
        self.assertEqual(2, args.verbose)
