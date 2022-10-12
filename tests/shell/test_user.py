"""Tests for the ``User`` class"""

from unittest import TestCase

from quota_notifier.shell import User


class UserInfo(TestCase):
    """Test the automatic identification of user metadata"""

    def test_root(self) -> None:
        """Test fetching user information for user ``root``"""

        user = User('root')
        self.assertEqual(user.username, 'root')
        self.assertEqual(user.uid, 0)
        self.assertEqual(user.group, 'root')
        self.assertEqual(user.gid, 0)
