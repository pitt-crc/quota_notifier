"""Tests for the ``Notification`` class."""

from unittest import TestCase

from app.orm import Notification


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

    def test_not_nullable(self) -> None:
        """Test required columns are not nullable"""

        for column in self.required_columns:
            self.assertFalse(column.nullable, f'Column {column} should not be nullable')
