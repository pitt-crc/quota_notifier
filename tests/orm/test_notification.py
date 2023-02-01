"""Tests for the ``Notification`` class."""

from unittest import TestCase

from sqlalchemy import select

from quota_notifier.orm import DBConnection, Notification


class ThresholdValidation(TestCase):
    """Test value validation for the ``threshold`` column"""

    def test_value_is_assigned(self) -> None:
        """Test the validated value is assigned to the table instance"""

        threshold = 50
        notification = Notification(threshold=threshold)
        self.assertEqual(threshold, notification.threshold)

    def test_error_on_out_of_range(self) -> None:
        """Check for a ``ValueError`` when threshold is not between 0 and 100"""

        with self.assertRaises(ValueError):
            Notification(threshold=-1)

        with self.assertRaises(ValueError):
            Notification(threshold=101)

    def test_boundary_values(self) -> None:
        """Test the values 0 and 100 are treated as valid"""

        for threshold in (0, 100):
            notification = Notification(threshold=threshold)
            self.assertEqual(threshold, notification.threshold)


class RequiredFields(TestCase):
    """Test required fields are not nullable"""

    required_columns = (
        Notification.username,
        Notification.last_update,
        Notification.threshold,
        Notification.file_system,
    )

    def runTest(self) -> None:
        """Test required columns are not nullable"""

        for column in self.required_columns:
            self.assertFalse(column.nullable, f'Column {column} should not be nullable')


class UpdateOnConflict(TestCase):
    """Test records are updated on uniqueness conflict"""

    def setUp(self) -> None:
        """Set up an empty mock database"""

        DBConnection.configure('sqlite:///:memory:')

    def test_records_updated(self) -> None:
        """Test records with unique username/filesystem pairs are replaced on insert"""

        with DBConnection.session() as session:
            session.add(Notification(username='user', file_system='fs1', threshold=10))
            session.commit()

        with DBConnection.session() as session:
            session.add(Notification(username='user', file_system='fs1', threshold=20))
            session.commit()

        with DBConnection.session() as session:
            records = session.execute(select(Notification)).scalars().all()

            self.assertEqual(1, len(records))
            self.assertEqual('user', records[0].username)
            self.assertEqual('fs1', records[0].file_system)
            self.assertEqual(20, records[0].threshold)
