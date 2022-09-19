"""Temporary file so the test suite CI has something to run.

Delete after real tests are written
"""

from unittest import TestCase

from app.main import Parser


class SubparsersRequired(TestCase):
    """Test a subparser is required by the commandline parser"""

    def test_is_required(self) -> None:
        """Test the subparser argument is marked as required"""

        parser = Parser()
        self.assertTrue(parser.subparsers.required)
