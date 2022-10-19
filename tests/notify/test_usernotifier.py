"""Tests for the ``UserNotifier`` class"""

import os
import pwd
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import select

from quota_notifier.disk_utils import GenericQuota
from quota_notifier.notify import UserNotifier
from quota_notifier.orm import DBConnection, Notification
from quota_notifier.settings import ApplicationSettings, FileSystemSchema
from quota_notifier.shell import User


class GetUsers(TestCase):
    """Test the fetching of usernames to notify"""

    def tearDown(self) -> None:
        """Reset any modifications to application settings after each test"""

        ApplicationSettings.configure()

    def test_includes_all_users(self) -> None:
        """Test all users are returned by default"""

        returned_users = [user.username for user in UserNotifier().get_users()]
        all_users = [user.pw_name for user in pwd.getpwall()]
        self.assertListEqual(all_users, returned_users)

    def test_blacklisted_users_excluded(self) -> None:
        """Test blacklisted users are not included in returned values"""

        all_users = [user.pw_name for user in pwd.getpwall()]
        self.assertIn('root', all_users)

        ApplicationSettings.configure(blacklist=['root'])
        returned_users = [user.username for user in UserNotifier().get_users()]
        self.assertNotIn('root', returned_users)


class GetUserQuotas(TestCase):

    def setUp(self) -> None:
        # Register the current directory with the application
        self.current_dir = Path(__file__).parent
        self.mock_file_system = FileSystemSchema(name='test', path=self.current_dir, type='generic')
        ApplicationSettings.configure(file_systems=[self.mock_file_system])

        # Create a subdirectory matching the current user's group
        self.current_user = User(os.getlogin())
        self.temp_dir = self.current_dir / self.current_user.group
        self.temp_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        """Restore application settings and remove temporary directories"""

        ApplicationSettings.configure()
        self.temp_dir.rmdir()

    def test_quota_matches_user(self) -> None:
        quota = next(UserNotifier().get_user_quotas(self.current_user))
        self.assertEqual(self.current_user, quota.user)

    def test_path_is_customized(self) -> None:
        quota = next(UserNotifier().get_user_quotas(self.current_user))
        self.assertEqual(self.current_user.group, quota.path.name)


class GetLastThreshold(TestCase):
    """Test fetching a quota's last notification threshold"""

    def test_missing_notification_history(self) -> None:
        """Test the first return value is ``None`` for a missing notification history"""

        quota = GenericQuota(name='fake', path=Path('/'), user=User('fake'), size_used=0, size_limit=100)
        threshold = UserNotifier.get_next_threshold(quota)
        self.assertIsNone(threshold)

    def test_matches_notification_history(self) -> None:
        """Test the first return matches the notification history"""

        test_path = '/'
        test_user = User('user1')
        test_filesystem = 'filesystem1'
        test_threshold = ApplicationSettings.get('thresholds')[0]

        DBConnection.configure(url='sqlite:///:memory:')
        with DBConnection.session() as session:
            session.add(Notification(
                username=test_user.username,
                file_system=test_filesystem,
                threshold=test_threshold
            ))
            session.commit()

        quota = GenericQuota(test_filesystem, test_path, test_user, 0, 100)
        threshold = UserNotifier.get_last_threshold(session, quota)
        self.assertEqual(test_threshold, threshold)


class GetNextThreshold(TestCase):
    """Test determination of the next notification threshold"""

    def test_usage_below_minimum_thresholds(self) -> None:
        """Test return is ``None`` when usage is below the minimum threshold"""

        quota = GenericQuota('filesystem1', Path('/'), User('user1'), 0, 100)
        self.assertIsNone(UserNotifier.get_next_threshold(quota))

    def test_usage_at_thresholds(self) -> None:
        """Test return matches a threshold when usage equals a threshold"""

        thresholds = ApplicationSettings.get('thresholds')

        quota = GenericQuota('filesystem1', Path('/'), User('user1'), thresholds[0], 100)
        self.assertEqual(thresholds[0], UserNotifier.get_next_threshold(quota))

        quota = GenericQuota('filesystem1', Path('/'), User('user1'), thresholds[-1], 100)
        self.assertEqual(thresholds[-1], UserNotifier.get_next_threshold(quota))

    def test_usage_between_thresholds(self) -> None:
        """Test return is the lower threshold when usage is between two thresholds"""

        thresholds = ApplicationSettings.get('thresholds')
        usage = (thresholds[0] + thresholds[1]) // 2
        quota = GenericQuota('filesystem1', Path('/'), User('user1'), usage, 100)
        self.assertEqual(thresholds[0], UserNotifier.get_next_threshold(quota))

    def test_usage_above_max_threshold(self) -> None:
        """Test return is the maximum threshold when usage exceeds the maximum threshold"""

        max_threshold = max(ApplicationSettings.get('thresholds'))
        usage = max_threshold + 1
        quota = GenericQuota('filesystem1', Path('/'), User('user1'), usage, 100)
        self.assertEqual(max_threshold, UserNotifier.get_next_threshold(quota))


@patch('quota_notifier.notify.SMTP')
class NotificationHistory(TestCase):
    """Test database updates when calling ``notify_user``"""

    def setUp(self) -> None:
        """Set up a mock user and mock DB"""

        self.mock_user = User('mock')
        self.mock_file_system = 'fs1'
        self.query = select(Notification).where(Notification.username == self.mock_user.username)

        DBConnection.configure('sqlite:///:memory:')

    def create_db_entry(self, threshold: int) -> None:
        """Create a database record representing a previous notification

        Args:
            threshold: The threshold of the notification
        """

        with DBConnection.session() as session:
            session.add(Notification(
                username=self.mock_user.username,
                file_system=self.mock_file_system,
                threshold=threshold
            ))
            session.commit()

    def run_application(self, usage):
        """Run the ``UserNotifier().notify_user`` method as if the user has utilized the given usage

        Args:
            usage: Storage quota usage between 0 and 100
        """

        test_quota = GenericQuota(self.mock_file_system, Path('/'), self.mock_user, size_used=usage, size_limit=100)
        with patch('quota_notifier.notify.UserNotifier.get_user_quotas', return_value=[test_quota]):
            UserNotifier().notify_user(self.mock_user)

    def test_old_notifications_deleted(self, *args) -> None:
        """Test old notifications are deleted from the database"""

        # Create a notification history for a low threshold
        lowest_threshold = ApplicationSettings.get('thresholds')[0]
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
        lowest_threshold = ApplicationSettings.get('thresholds')[0]
        self.create_db_entry(lowest_threshold)

        # Process a new notification for a higher threshold
        highest_threshold = ApplicationSettings.get('thresholds')[-1]
        self.run_application(usage=highest_threshold)

        # Check the notification history was updated
        with DBConnection.session() as session:
            db_record = session.execute(self.query).scalars().first()
            self.assertEqual(highest_threshold, db_record.threshold)

    def test_reduced_quotas_updated(self, *args) -> None:
        """Test records are updated for quotas that have dropped to a new threshold"""

        # Create a notification history for a high threshold
        highest_threshold = ApplicationSettings.get('thresholds')[-1]
        self.create_db_entry(highest_threshold)

        # Process a new notification for a lower threshold
        lowest_threshold = ApplicationSettings.get('thresholds')[0]
        self.run_application(usage=lowest_threshold)

        # Check the notification history was updated

        with DBConnection.session() as session:
            db_record = session.execute(self.query).scalars().first()
            self.assertEqual(lowest_threshold, db_record.threshold)
