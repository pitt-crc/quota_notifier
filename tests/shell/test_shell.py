"""Tests for the ``Shell`` class"""

from unittest import TestCase

from app.shell import ShellCmd


class EmptyCommandError(TestCase):
    """Test an error is raised if the command string is empty"""

    def runTest(self) -> None:
        """Execute the test"""

        with self.assertRaises(ValueError):
            ShellCmd('')


class FileDescriptors(TestCase):
    """Test STDOUT and STDERR are captured and returned"""

    def test_capture_on_success(self) -> None:
        """Test for command writing to STDOUT"""

        test_message = 'hello world'
        cmd = ShellCmd(f"echo '{test_message}'")
        self.assertEqual(test_message, cmd.out)
        self.assertFalse(cmd.err)

    def test_capture_on_err(self) -> None:
        """Test for command writing to STDERR"""

        cmd = ShellCmd("ls fake_dr")
        self.assertFalse(cmd.out)
        self.assertTrue(cmd.err)

    def test_output_decoded(self) -> None:
        """Test file descriptor values are decoded"""

        cmd = ShellCmd('echo hello world')
        self.assertIsInstance(cmd.out, str)
        self.assertIsInstance(cmd.err, str)
