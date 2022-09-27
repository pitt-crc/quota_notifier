"""Tests for the ``UserNotifier`` class"""
import pwd
from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import select

from app.disk_utils import GenericQuota
from app.notify import UserNotifier
from app.orm import DBConnection, Notification
from app.settings import ApplicationSettings
from app.shell import User


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


class GetLastThreshold(TestCase):
    """Test fetching a quota's last notification threshold"""

    def test_missing_notification_history(self) -> None:
        """Test the first return value is ``None`` for a missing notification history"""

        quota = GenericQuota(name='fake', user=User('fake'), size_used=0, size_limit=100)
        threshold = UserNotifier.get_next_threshold(quota)
        self.assertIsNone(threshold)

    def test_matches_notification_history(self) -> None:
        """Test the first return matches the notification history"""

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

        quota = GenericQuota(test_filesystem, test_user, 0, 100)
        threshold = UserNotifier.get_last_threshold(session, quota)
        self.assertEqual(test_threshold, threshold)


class GetNextThreshold(TestCase):
    """Test determination of the next notification threshold"""

    def test_usage_below_minimum_thresholds(self) -> None:
        """Test return is ``None`` when usage is below the minimum threshold"""

        quota = GenericQuota('filesystem1', User('user1'), 0, 100)
        self.assertIsNone(UserNotifier.get_next_threshold(quota))

    def test_usage_at_thresholds(self) -> None:
        """Test return matches a threshold when usage equals a threshold"""

        thresholds = ApplicationSettings.get('thresholds')

        quota = GenericQuota('filesystem1', User('user1'), thresholds[0], 100)
        self.assertEqual(thresholds[0], UserNotifier.get_next_threshold(quota))

        quota = GenericQuota('filesystem1', User('user1'), thresholds[-1], 100)
        self.assertEqual(thresholds[-1], UserNotifier.get_next_threshold(quota))

    def test_usage_between_thresholds(self) -> None:
        """Test return is the lower threshold when usage is between two thresholds"""

        thresholds = ApplicationSettings.get('thresholds')
        usage = (thresholds[0] + thresholds[1]) // 2
        quota = GenericQuota('filesystem1', User('user1'), usage, 100)
        self.assertEqual(thresholds[0], UserNotifier.get_next_threshold(quota))

    def test_usage_above_max_threshold(self) -> None:
        """Test return is the maximum threshold when usage exceeds the maximum threshold"""

        max_threshold = max(ApplicationSettings.get('thresholds'))
        usage = max_threshold + 1
        quota = GenericQuota('filesystem1', User('user1'), usage, 100)
        self.assertEqual(max_threshold, UserNotifier.get_next_threshold(quota))


@patch('app.email.SMTP')
class NotificationHistory(TestCase):
    """Test database updates when calling ``notify_user``"""

    def setUp(self) -> None:
        """Set up a mock user and mock DB"""

        self.mock_user = User('mock')
        self.mock_file_system = 'fs1'

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

    def test_old_notifications_deleted(self, *args) -> None:
        """Test old notifications are deleted from the database"""

        # Create a notification history for a low threshold
        lowest_threshold = ApplicationSettings.get('thresholds')[0]
        self.create_db_entry(lowest_threshold)

        # Process a new notification for a usage below the minimum threshold
        test_quota = GenericQuota(name=self.mock_file_system, user=self.mock_user, size_used=0, size_limit=100)
        with patch('app.notify.UserNotifier.get_user_quotas', return_value=[test_quota]):
            UserNotifier().notify_user(self.mock_user)

        # Check the notification history was deleted
        query = select(Notification).where(Notification.username == self.mock_user.username)
        with DBConnection.session() as session:
            db_records = session.execute(query).scalars().all()
            self.assertListEqual([], db_records)

    def test_new_notification_saved(self, *args) -> None:
        """Test new notifications are recorded in the database"""

        # Create a notification history for a low threshold
        lowest_threshold = ApplicationSettings.get('thresholds')[0]
        self.create_db_entry(lowest_threshold)

        # Process a new notification for a higher threshold
        highest_threshold = ApplicationSettings.get('thresholds')[-1]
        test_quota = GenericQuota(name=self.mock_file_system, user=self.mock_user, size_used=highest_threshold, size_limit=100)
        with patch('app.notify.UserNotifier.get_user_quotas', return_value=[test_quota]):
            UserNotifier().notify_user(self.mock_user)

        # Check the notification history was updated
        query = select(Notification).where(Notification.username == self.mock_user.username)
        with DBConnection.session() as session:
            record = session.execute(query).scalars().first()
            self.assertEqual(highest_threshold, record.threshold)

    def test_reduced_quotas_updated(self, *args) -> None:
        """Test records are updated for quotas that have dropped to a new threshold"""

        # Create a notification history for a high threshold
        highest_threshold = ApplicationSettings.get('thresholds')[-1]
        self.create_db_entry(highest_threshold)

        # Process a new notification for a lower threshold
        lowest_threshold = ApplicationSettings.get('thresholds')[0]
        test_quota = GenericQuota(name=self.mock_file_system, user=self.mock_user, size_used=lowest_threshold, size_limit=100)
        with patch('app.notify.UserNotifier.get_user_quotas', return_value=[test_quota]):
            UserNotifier().notify_user(self.mock_user)

        # Check the notification history was updated
        query = select(Notification).where(Notification.username == self.mock_user.username)
        with DBConnection.session() as session:
            db_record = session.execute(query).scalars().first()
            self.assertEqual(lowest_threshold, db_record.threshold)
