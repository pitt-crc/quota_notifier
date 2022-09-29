"""Tools for running commands and fetching user data from the underlying system shell.

Module Contents
---------------
"""

from shlex import split
from subprocess import PIPE, Popen
from typing import Optional

from app.settings import ApplicationSettings


class ShellCmd:
    """Execute commands using the underlying shell

    Outputs to STDOUT and STDERR are exposed via the ``out`` and ``err``
    attributes respectively.
    """

    def __init__(self, cmd: str, timeout: Optional[int] = ApplicationSettings.get('disk_timeout')) -> None:
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
    """Fetch identifying information for a given username"""

    def __init__(self, username: str) -> None:
        """Fetch identifying information for the given username

        Args:
            username: The name of the user
        """

        self._username = username

    @property
    def username(self) -> str:
        """Return the instance username"""

        return self._username

    @property
    def group(self) -> str:
        """Fetch and return the users group name"""

        return ShellCmd(f"id -gn {self._username}").out

    @property
    def uid(self) -> int:
        """Fetch and return the users user id"""

        return int(ShellCmd(f"id -u {self._username}").out)

    @property
    def gid(self) -> int:
        """Fetch and return the users group id"""

        return int(ShellCmd(f"id -g {self._username}").out)
