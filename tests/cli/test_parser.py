"""Temporary file so the test suite CI has something to run.

Delete after real tests are written
"""

from unittest import TestCase

from app.main import Application, Parser


class SubparsersRequired(TestCase):
    """Test a subparser is required by the commandline parser"""

    def test_is_required(self) -> None:
        """Test the subparser argument is marked as required"""

        parser = Parser()
        self.assertTrue(parser.subparsers.required)


class SubparserMapping(TestCase):
    """Test the mapping of subparsers to executable functions"""

    def test_notify_subparser(self) -> None:
        """Test the ``notify`` parser maps to the ``send_notifications`` function"""

        args = Parser().parse_args(['notify'])
        self.assertEqual(args.action, Application.send_notifications)
