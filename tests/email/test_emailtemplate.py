"""Tests for the ``EmailTemplate`` class."""

from unittest import TestCase

from app.disk_utils import GenericQuota
from app.email import EmailTemplate


class TemplateFormatting(TestCase):
    """Test the formatting of the email template with quota information"""

    @classmethod
    def setUpClass(self) -> None:
        """Create a formatted email template"""

        self.quota = GenericQuota('testquota', size_used=10, size_limit=100)
        self.template = EmailTemplate([self.quota])

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
