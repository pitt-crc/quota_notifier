"""Tests for the ``Parser`` class."""

from unittest import TestCase

from quota_notifier.cli import Parser


class ParserHelpData(TestCase):
    """Test the parser is configured with help data"""

    def test_custom_prog_name(self) -> None:
        """Test the application name is set to ``notifier``"""

        self.assertEqual('notifier', Parser().prog)

    def test_has_description(self) -> None:
        """Test the application description is not empty"""

        self.assertTrue(Parser().description)


class ValidateOption(TestCase):
    """Test parsing of the ``--validate`` option"""

    def test_defaults_to_false(self) -> None:
        """Test the ``validate`` flag defaults to ``False``"""

        args = Parser().parse_args([])
        self.assertFalse(args.validate)

    def test_stores_true(self) -> None:
        """Test the ``validate`` flag stores true when specified"""

        args = Parser().parse_args(['--validate'])
        self.assertTrue(args.validate)


class DebugOption(TestCase):
    """Test parsing of the ``--debug`` option"""

    def test_defaults_to_false(self) -> None:
        """Test the ``debug`` flag defaults to ``False``"""

        args = Parser().parse_args([])
        self.assertFalse(args.debug)

    def test_stores_true(self) -> None:
        """Test the ``debug`` flag stores true when specified"""

        args = Parser().parse_args(['--debug'])
        self.assertTrue(args.debug)


class VerboseOption(TestCase):
    """Test parsing of the ``--verbose`` option"""

    def test_defaults_to_zero(self) -> None:
        """Test the ``verbose`` value is zero when not specified"""

        args = Parser().parse_args([])
        self.assertEqual(0, args.verbose)

    def test_flag_counting(self) -> None:
        """Test verbose flags are counted as integers"""

        for num_flags in (1, 2, 3):
            flag = '-' + num_flags * 'v'
            args = Parser().parse_args([flag])
            self.assertEqual(num_flags, args.verbose)

    def test_many_flags_accepted(self) -> None:
        """Test several verbose flags are accepted beyond the reasonable limit"""

        args = Parser().parse_args(['-vvvvvvvvvvvvvvvvvvvv'])
        self.assertEqual(20, args.verbose)
