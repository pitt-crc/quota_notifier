"""Tests for the ``DBConnection`` class"""

from tempfile import NamedTemporaryFile
from unittest import TestCase

from quota_notifier.orm import DBConnection


class DBConfiguration(TestCase):
    """Test the configuration of the DB connection via the ``configure`` method"""

    def test_engine_is_configured(self) -> None:
        """Test the DB engine reflects the DB configuration"""

        with NamedTemporaryFile(suffix='._db') as temp:
            custom_url = f'sqlite:///{temp.name}'
            DBConnection.configure(custom_url)
            session = DBConnection.session()  # Calling session establishes a connection with the DB

        # Make sure the DB engine is pointing to the new URL
        self.assertEqual(custom_url, DBConnection.url, '`DBConnection.url` not set to correct URL')
        self.assertEqual(
            custom_url, DBConnection.engine.url.render_as_string(),
            'Incorrect URL for `engine` attribute')

        # Make sure session objects are tied to the correct engine
        self.assertEqual(
            DBConnection.engine, session.get_bind(),
            '`DBConnection.session` bound to incorrect engine')
