"""Tests for the ``DBConnection`` class"""

from tempfile import NamedTemporaryFile
from unittest import TestCase

from quota_notifier.orm import DBConnection


class DBConfiguration(TestCase):
    """Test configuration of the DB connection via the ``configure`` method"""

    def test_connection_is_configured(self) -> None:
        """Test class attributes are set to reflect DB configuration"""

        # Use a temporary file to ensure we are using a unique URL
        with NamedTemporaryFile(suffix='._db') as temp:
            custom_url = f'sqlite:///{temp.name}'
            DBConnection.configure(custom_url)

        # Make sure the DB engine is pointing to the new URL
        self.assertIsNotNone(DBConnection.url)
        self.assertEqual(custom_url, DBConnection.url, '`DBConnection.url` not set to correct URL')

        self.assertIsNotNone(DBConnection.engine)
        self.assertEqual(
            custom_url, DBConnection.engine.url.render_as_string(),
            'Incorrect URL for `engine` attribute')

        self.assertIsNotNone(DBConnection.connection)
        self.assertEqual(
            DBConnection.engine, DBConnection.connection.engine,
            '`DBConnection.connection` bound to incorrect engine')

        self.assertIsNotNone(DBConnection.session)
        self.assertEqual(
            DBConnection.engine, DBConnection.session.kw['bind'],
            '`DBConnection.session` bound to incorrect engine')
