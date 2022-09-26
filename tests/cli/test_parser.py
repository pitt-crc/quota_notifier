"""Tests for the ``Parser`` class."""

from unittest import TestCase

from app.cli import DEFAULT_SETTINGS, Parser


class ParserHelpData(TestCase):
    """Test the parser is configured with help data"""

    def test_custom_prog_name(self) -> None:
        """Test the application name is configured as ``notifier``"""

        self.assertEqual('notifier', Parser().prog)

    def test_has_description(self) -> None:
        """Test the application description is not empty"""

        self.assertTrue(Parser().description)


class ParserDefaults(TestCase):
    """Test the value of default arguments"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.args = Parser().parse_args([])

    def test_default_config_path(self) -> None:
        """Test the default settings path matches globally defined values"""

        self.assertEqual(DEFAULT_SETTINGS, self.args.settings)

    def test_check_flag_false(self) -> None:
        """Test the ``check`` flag defaults to ``False``"""

        self.assertFalse(self.args.check)
