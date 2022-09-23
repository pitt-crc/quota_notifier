"""Tools for running commands and fetching user data from the underlying system shell.

Module Contents
---------------
"""

from shlex import split
from subprocess import PIPE, Popen
from typing import Optional


class ShellCmd:
    """Execute commands using the underlying shell

    Outputs to STDOUT and STDERR are exposed via the ``out`` and ``err``
    attributes respectively.
    """

    def __init__(self, cmd: str, timeout: Optional[int] = None) -> None:
        """Execute the given command in the underlying shell

        Args:
            cmd: The command to run
            timeout: Timeout if command does not exit in given number of seconds

        Raises:
            ValueError: When the ``cmd`` argument is empty
            TimeoutExpired: If the command times out
        """

        if not cmd:
            raise ValueError('Command string cannot be empty')

        out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate(timeout=timeout)
        self.out = out.decode("utf-8").strip()
        self.err = err.decode("utf-8").strip()


class User:
    """Fetch identifying information for a given username

    Attributes:
        username: The user's username
        group:  The user's primary group name
        uid: The user identifier
        gid: The primary group identifier
    """

    def __init__(self, username: str) -> None:
        """Fetch identifying information for the given username

        Args:
            username: The name of the user
        """

        self.username = username
        self.group = ShellCmd(f"id -gn {username}").out
        self.uid = ShellCmd(f"id -u {username}").out
        self.gid = ShellCmd(f"id -g {username}").out
