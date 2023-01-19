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


class StringRepresentation(TestCase):
    """Test casting User objects as strings"""

    def test_matches_username(self) -> None:
        """Test the string representation matches the username"""

        username = 'some_user'
        user = User(username)
        self.assertEqual(username, str(user))


class Equality(TestCase):
    """Test the User class supports the equal opperation"""

    def test_equal_users(self) -> None:
        """Test users with the same username are equal"""

        self.assertTrue(User('root') == User('root'))

    def test_unequal_users(self) -> None:
        """Test users with the different usernames are not equal"""

        self.assertFalse(User('user1') == User('user2'))
