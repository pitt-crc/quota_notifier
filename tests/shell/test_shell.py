"""Tests for the ``Shell`` class"""

import subprocess
from unittest import TestCase

from quota_notifier.shell import ShellCmd


class ErrorOnProhibitedCharacters(TestCase):
    """Test an error is raised if special characters are used in the piped commands"""

    def runTest(self) -> None:
        """Execute the test"""

        for char in ShellCmd.prohibited_characters:
            with self.assertRaisesRegex(RuntimeError, 'Special characters are not allowed'):
                ShellCmd(char)


class EmptyCommandError(TestCase):
    """Test an error is raised if the command string is empty"""

    def runTest(self) -> None:
        """Execute the test"""

        with self.assertRaisesRegex(ValueError, 'Command string cannot be empty'):
            ShellCmd('')

        with self.assertRaisesRegex(ValueError, 'Command string cannot be empty'):
            ShellCmd(' ')


class FileDescriptors(TestCase):
    """Test STDOUT and STDERR are captured as attributes"""

    def test_capture_on_success(self) -> None:
        """Test STDOUT is captured in the ``.out`` attribute"""

        test_message = 'hello world'
        cmd = ShellCmd(f"echo '{test_message}'")
        self.assertEqual(test_message, cmd.out)
        self.assertFalse(cmd.err)

    def test_capture_on_err(self) -> None:
        """Test STDERR is captured in the ``.err`` attribute"""

        cmd = ShellCmd("ls fake_dr")
        self.assertFalse(cmd.out)
        self.assertTrue(cmd.err)

    def test_output_decoded(self) -> None:
        """Test file descriptor values are decoded"""

        cmd = ShellCmd('echo hello world')
        self.assertIsInstance(cmd.out, str)
        self.assertIsInstance(cmd.err, str)


class Timeout(TestCase):
    """Test the timeout argument is enforced"""

    def test_timeout_zero(self) -> None:
        """Test the command times out immediately when passed zero seconds"""

        with self.assertRaises(subprocess.TimeoutExpired):
            ShellCmd('echo', timeout=0)

    def test_command_times_out(self) -> None:
        """Test the command times out"""

        with self.assertRaises(subprocess.TimeoutExpired):
            ShellCmd('sleep 5', timeout=2)
