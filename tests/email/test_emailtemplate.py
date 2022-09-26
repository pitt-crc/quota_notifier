"""Tests for the ``EmailTemplate`` class."""

from unittest import TestCase
from unittest.mock import call, patch

from app.disk_utils import GenericQuota
from app.email import EmailTemplate
from app.settings import ApplicationSettings
from app.shell import User


class TemplateFormatting(TestCase):
    """Test the formatting of the email template with quota information"""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a formatted email template"""

        cls.quota = GenericQuota('testquota', User('test_user'), size_used=10, size_limit=100)
        cls.template = EmailTemplate([cls.quota])

    def test_starts_with_header(self) -> None:
        """Test the formatted message starts with the template header"""

        self.assertTrue(
            self.template.message.startswith(EmailTemplate.header),
            'Email message does not start with template header.')

    def test_ends_with_footer(self) -> None:
        """Test the formatted message ends with the template footer"""

        self.assertTrue(
            self.template.message.endswith(EmailTemplate.footer),
            'Email message does not end with template footer.')


class MessageSending(TestCase):
    """Tests for sending emails via an SMTP server"""

    def setUp(self) -> None:
        """Create a formatted email template"""

        self.quota = GenericQuota('testquota', User('test_user'), size_used=10, size_limit=100)
        self.template = EmailTemplate([self.quota])

    @patch('smtplib.SMTP')
    def test_fields_are_set(self, mock_smtp) -> None:
        """Test email fields (to, from, subject, body) are set in the sent email"""

        to_address = 'fake_recipient@fake_domain.com'
        sent_message = self.template.send(to_address, mock_smtp)

        # The rstrip removes a newline character that is added automatically in the sent message
        body = sent_message.get_body().get_content().rstrip()
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


class SendingViaUsername(TestCase):
    """Test sending emails via username instead of address"""

    @patch('smtplib.SMTP')
    def test_domain_matches_settings(self, mock_smtp) -> None:
        """Test the generated destination address matches application settings"""

        user = User('myuser')
        sent_message = EmailTemplate([]).send_to_user(user, mock_smtp)
        username, domain = sent_message['To'].split('@')

        self.assertEqual(user.username, username)
        self.assertEqual('@' + domain, ApplicationSettings.get('email_domain'))
