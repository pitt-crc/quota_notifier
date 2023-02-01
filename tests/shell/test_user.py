"""Tests for the ``User`` class"""

import pwd
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


class IterAllUsers(TestCase):
    """Test the ``iter_all_users`` method"""

    def test_all_users_returned(self) -> None:
        """Test the iterator returns all users on the system"""

        all_usernames = {user_entry.pw_name for user_entry in pwd.getpwall()}
        returned_users = [user.username for user in User.iter_all_users()]
        self.assertCountEqual(all_usernames, returned_users)

    def test_returned_as_user_objects(self) -> None:
        """Test users are returned as ``User`` objects"""

        for user in User.iter_all_users():
            self.assertIsInstance(user, User)


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
