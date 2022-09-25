"""Tests for the ``Parser`` class."""

from unittest import TestCase

from app.cli import Parser


class ParserHelpData(TestCase):
    """Test the parser is configured with help data"""

    def test_custom_prog_name(self) -> None:
        """Test the application name is configured as ``notifier``"""

        self.assertEqual('notifier', Parser().prog)
