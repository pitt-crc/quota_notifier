"""Tests for the ``UserNotifier`` class"""

from unittest import TestCase

from app.orm import DBConnection, Notification
from app.settings import app_settings


class ThresholdIdentification(TestCase):
    """Test the determination of notification thresholds from notification history"""

    @classmethod
    def setUpClass(cls) -> None:
        """Configure a temporary database"""

        DBConnection.configure(url='sqlite:///:memory:')

    def setUp(self) -> None:
        """Populate database with testing data"""

        with DBConnection.session() as session:
            session.add(Notification(
                username='user1', file_system='filesystem1', threshold=app_settings.thresholds[0]
            ))
            session.commit()
