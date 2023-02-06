"""Tests for the ``UserNotifier`` class"""

import os
import pwd
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import select

from quota_notifier.disk_utils import GenericQuota
from quota_notifier.notify import UserNotifier
from quota_notifier.orm import DBConnection, Notification
from quota_notifier.settings import ApplicationSettings, FileSystemSchema
from quota_notifier.shell import User


class GetUsers(TestCase):
    """Test the ``get_users`` method"""

    def tearDown(self) -> None:
        """Reset any modifications to application settings after each test"""

        ApplicationSettings.reset_defaults()

    def test_empty_blacklists(self) -> None:
        """Test all users are returned for empty blacklists"""

        ApplicationSettings.set(uid_blacklist=[], gid_blacklist=[])
        returned_users = [user.username for user in UserNotifier().get_users()]
        all_users = [user.pw_name for user in pwd.getpwall()]
        self.assertListEqual(all_users, returned_users)

    def test_blacklisted_by_uid(self) -> None:
        """Test blacklisted UIDs are not included in returned values"""

        ApplicationSettings.set(uid_blacklist={0}, gid_blacklist=set())
        returned_uids = [user.uid for user in UserNotifier().get_users()]
        self.assertNotIn(0, returned_uids)

    def test_blacklisted_by_gid(self) -> None:
        """Test blacklisted GIDs are not included in returned values"""

        ApplicationSettings.set(uid_blacklist=set(), gid_blacklist={0})
        returned_gids = [user.gid for user in UserNotifier().get_users()]
        self.assertNotIn(0, returned_gids)

    def test_blacklisted_by_uid_range(self) -> None:
        """Test blacklisted UID ranges are not included in returned values"""

        ApplicationSettings.set(uid_blacklist={(0, 100)}, gid_blacklist=set())
        returned_uids = [user.uid for user in UserNotifier().get_users()]
        self.assertNotIn(0, returned_uids)

    def test_blacklisted_by_gid_range(self) -> None:
        """Test blacklisted GID ranges are not included in returned values"""

        ApplicationSettings.set(uid_blacklist=set(), gid_blacklist={(0, 100)})
        returned_gids = [user.gid for user in UserNotifier().get_users()]
        self.assertNotIn(0, returned_gids)


class GetUserQuotas(TestCase):
    """Test the fetching of user quotas via the ``get_user_quotas`` method"""

    def setUp(self) -> None:
        """Create and register a temporary directory to generate quota objects for"""

        # Register a temporary directory with the application
        self.temp_dir = TemporaryDirectory()
        self.mock_file_system = FileSystemSchema(name='test', path=self.temp_dir.name, type='generic', thresholds=[50])
        ApplicationSettings.set(file_systems=[self.mock_file_system])

        # Create a subdirectory matching the current user's group
        self.test_user = User(os.getenv('USER'))
        group_dir = Path(self.temp_dir.name) / self.test_user.group
        group_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        """Restore application settings and remove temporary directories"""

        ApplicationSettings.reset_defaults()
        self.temp_dir.cleanup()

    def test_quota_matches_user(self) -> None:
        """Test the returned quotas match the given user"""

        quota = next(UserNotifier().get_user_quotas(self.test_user))
        self.assertEqual(self.test_user, quota.user)

    def test_path_is_customized(self) -> None:
        """Test the returned quotas match the group directory"""

        quota = next(UserNotifier().get_user_quotas(self.test_user))
        self.assertEqual(self.test_user.group, quota.path.name)


class GetLastThreshold(TestCase):
    """Test fetching a quota's last notification threshold via the ``get_last_threshold`` method"""

    def setUp(self) -> None:
        """Run tests against a temporary database in memory"""

        ApplicationSettings.set(db_url='sqlite:///:memory:')

    def test_missing_notification_history(self) -> None:
        """Test the return value is ``None`` for a missing notification history"""

        quota = GenericQuota(name='fake', path=Path('/'), user=User('fake'), size_used=0, size_limit=100)
        threshold = UserNotifier.get_last_threshold(DBConnection.session(), quota)
        self.assertIsNone(threshold)

    def test_existing_notification_history(self) -> None:
        """Test the return value matches information from the database"""

        # Test data for a previous notification at 50% usage
        test_path = '/'
        test_user = User('user1')
        test_filesystem = 'filesystem1'
        test_threshold = 50

        # Populate database with test data
        with DBConnection.session() as session:
            session.add(Notification(
                username=test_user.username,
                file_system=test_filesystem,
                threshold=test_threshold
            ))
            session.commit()

        # Assume 0% usage and fetch last notification threshold
        quota = GenericQuota(test_filesystem, test_path, test_user, 0, 100)
        threshold = UserNotifier.get_last_threshold(session, quota)
        self.assertEqual(test_threshold, threshold)


class GetNextThreshold(TestCase):
    """Test determination of the next notification threshold"""

    def setUp(self) -> None:
        """Set up testing constructs against a temporary DB in memory

        Configures a single file system in application settings called test with
        notification thresholds at 50 and 75 percent.
        """

        ApplicationSettings.reset_defaults()
        ApplicationSettings.set(db_url='sqlite:///:memory:')

        self.test_file_system = FileSystemSchema(name='test', path='/', type='generic', thresholds=[50, 75])
        ApplicationSettings.set(file_systems=[self.test_file_system])

    def test_usage_below_minimum_thresholds(self) -> None:
        """Test return is ``None`` when usage is below the minimum threshold"""

        quota = GenericQuota(
            self.test_file_system.name,
            self.test_file_system.path,
            User('user1'),
            0,
            100)

        self.assertIsNone(UserNotifier.get_next_threshold(quota))

    def test_usage_at_thresholds(self) -> None:
        """Test return matches a threshold when usage equals a threshold"""

        expected_threshold = self.test_file_system.thresholds[0]
        quota = GenericQuota(
            self.test_file_system.name,
            self.test_file_system.path,
            User('user1'),
            expected_threshold,
            100)

        self.assertEqual(expected_threshold, UserNotifier.get_next_threshold(quota))

    def test_usage_between_thresholds(self) -> None:
        """Test return is the lower threshold when usage is between two thresholds"""

        lower_threshold = self.test_file_system.thresholds[0]
        upper_threshold = self.test_file_system.thresholds[1]
        median_usage = (lower_threshold + upper_threshold) // 2
        quota = GenericQuota(
            self.test_file_system.name,
            self.test_file_system.path,
            User('user1'),
            median_usage,
            100)

        self.assertEqual(lower_threshold, UserNotifier.get_next_threshold(quota))

    def test_usage_above_max_threshold(self) -> None:
        """Test return is the maximum threshold when usage exceeds the maximum threshold"""

        expected_threshold = self.test_file_system.thresholds[-1]
        quota = GenericQuota(
            self.test_file_system.name,
            self.test_file_system.path,
            User('user1'),
            expected_threshold + 10,
            100)

        self.assertEqual(expected_threshold, UserNotifier.get_next_threshold(quota))


@patch('quota_notifier.notify.SMTP')
class NotificationHistory(TestCase):
    """Test the database updates after calling ``notify_user``"""

    def setUp(self) -> None:
        """Set up testing constructs against a temporary DB in memory

        Configures a single file system in application settings called test with
        notification thresholds at 50 and 75 percent.
        """

        ApplicationSettings.reset_defaults()
        ApplicationSettings.set(db_url='sqlite:///:memory:')

        # Reusable database query for fetching user info
        self.mock_user = User('mock')
        self.query = select(Notification).where(Notification.username == self.mock_user.username)

        # Configure a mock file system with the parent applicaion
        self.mock_file_system = FileSystemSchema(name='test', path='/', type='generic', thresholds=[50, 75])
        ApplicationSettings.set(file_systems=[self.mock_file_system])

    def create_db_entry(self, threshold: int) -> None:
        """Create a database record representing a previous notification

        Args:
            threshold: The threshold of the notification
        """

        with DBConnection.session() as session:
            session.add(Notification(
                username=self.mock_user.username,
                file_system=self.mock_file_system.name,
                threshold=threshold
            ))
            session.commit()

    def run_application(self, usage):
        """Run the ``UserNotifier().notify_user`` method as if the user has utilized the given usage

        Args:
            usage: Storage quota usage between 0 and 100
        """

        test_quota = GenericQuota(
            self.mock_file_system.name,
            self.mock_file_system.path,
            self.mock_user,
            size_used=usage,
            size_limit=100)

        with patch('quota_notifier.notify.UserNotifier.get_user_quotas', return_value=[test_quota]):
            UserNotifier().notify_user(self.mock_user)

    def test_old_notifications_deleted(self, *args) -> None:
        """Test old notifications are deleted from the database"""

        # Create a notification history for a low threshold
        lowest_threshold = self.mock_file_system.thresholds[0]
        self.create_db_entry(lowest_threshold)

        # Process a new notification for a usage below the minimum threshold
        self.run_application(usage=0)

        # Check the notification history was deleted
        with DBConnection.session() as session:
            db_records = session.execute(self.query).scalars().all()
            self.assertListEqual([], db_records)

    def test_new_notification_saved(self, *args) -> None:
        """Test new notifications are recorded in the database"""

        # Create a notification history for a low threshold
        lowest_threshold = self.mock_file_system.thresholds[0]
        self.create_db_entry(lowest_threshold)

        # Process a new notification for a higher threshold
        highest_threshold = self.mock_file_system.thresholds[-1]
        self.run_application(usage=highest_threshold)

        # Check the notification history was updated
        with DBConnection.session() as session:
            db_record = session.execute(self.query).scalars().first()
            self.assertEqual(highest_threshold, db_record.threshold)

    def test_reduced_quotas_updated(self, *args) -> None:
        """Test records are updated for quotas that have dropped to a new threshold"""

        # Create a notification history for a high threshold
        highest_threshold = self.mock_file_system.thresholds[-1]
        self.create_db_entry(highest_threshold)

        # Process a new notification for a lower threshold
        lowest_threshold = self.mock_file_system.thresholds[0]
        self.run_application(usage=lowest_threshold)

        # Check the notification history was updated
        with DBConnection.session() as session:
            db_record = session.execute(self.query).scalars().first()
            self.assertEqual(lowest_threshold, db_record.threshold)
