"""Tests for the ``EmailTemplate`` class."""

from pathlib import Path
from unittest import TestCase
from unittest.mock import call, patch

from quota_notifier.disk_utils import GenericQuota
from quota_notifier.notify import EmailTemplate
from quota_notifier.settings import ApplicationSettings
from quota_notifier.shell import User


class TemplateFormatting(TestCase):
    """Test the formatting of the email template with quota information

    These tests don't enforce the overall formatting of the template, but do
    ensure all the necessary content is present.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Create a formatted email template"""

        cls.quota = GenericQuota(
            name='testquota',
            path=Path('/'),
            user=User('test_user'),
            size_used=10, size_limit=100)

        cls.template = EmailTemplate([cls.quota])

    def test_includes_quota_information(self) -> None:
        """Test the formatted message include quota information"""

        self.assertIn(str(self.quota), self.template.message)


class MessageSending(TestCase):
    """Tests for sending emails via an SMTP server"""

    def setUp(self) -> None:
        """Create a formatted email template"""

        self.quota = GenericQuota('testquota', Path('/'), User('test_user'), size_used=10, size_limit=100)
        self.template = EmailTemplate([self.quota])

    def tearDown(self) -> None:
        """Reset any modified application settings"""

        ApplicationSettings.reset_defaults()

    @patch('smtplib.SMTP')
    def test_fields_are_set(self, mock_smtp) -> None:
        """Test required email fields (to, from, subject, body) are included in the delivered email"""

        to_address = 'fake_recipient@fake_domain.com'
        sent_message = self.template.send(to_address, mock_smtp)

        # The rstrip removes a newline character that is added automatically in the delivered message
        body = sent_message.get_body().get_content()
        self.assertEqual(self.template.message, body)

        self.assertEqual(to_address, sent_message['To'])
        self.assertEqual(EmailTemplate.email_from, sent_message['From'])
        self.assertEqual(EmailTemplate.email_subject, sent_message['Subject'])

    @patch('smtplib.SMTP')
    def test_message_is_sent(self, mock_smtp) -> None:
        """Test the smtp server is given the email message to send"""

        email_message = self.template.send('to@address.com', mock_smtp)

        # Note that one of expected calls is ``call()`` from the __enter__ context manager
        self.assertEqual(
            mock_smtp.__enter__.mock_calls,
            [call(), call().send_message(email_message)]
        )

    @patch('smtplib.SMTP')
    def test_not_sent_on_debug(self, mock_smtp) -> None:
        """Test an email is not sent in debug mode"""

        ApplicationSettings.set(debug=True)
        self.template.send('to@address.com', mock_smtp)
        self.assertFalse(mock_smtp.mock_calls)


class SendingByUsername(TestCase):
    """Test sending emails via username instead of address"""

    @patch('smtplib.SMTP')
    def test_domain_matches_settings(self, mock_smtp) -> None:
        """Test the generated destination address matches application settings"""

        user = User('myuser')
        sent_message = EmailTemplate([]).send_to_user(user, mock_smtp)
        username, domain = sent_message['To'].split('@')

        self.assertEqual(user.username, username)
        self.assertEqual('@' + domain, ApplicationSettings.get('email_domain'))
