"""Temporary file so the test suite CI has something to run.

Delete after real tests are written
"""

from unittest import TestCase


class DUmmyTest(TestCase):
    """A placeholder test case"""

    def runTest(self) -> None:
        """This test will always pass"""
