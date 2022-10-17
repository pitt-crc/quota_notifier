"""Tools for running commands and fetching user data from the underlying system shell.

Module Contents
---------------
"""

import grp
import logging
import pwd
from shlex import split
from subprocess import PIPE, Popen
from typing import Optional

from quota_notifier.settings import ApplicationSettings


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

        logging.debug(f'running {cmd}')
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

        return grp.getgrgid(self.gid).gr_name

    @property
    def uid(self) -> int:
        """Fetch and return the users user id"""

        return pwd.getpwnam(self._username).pw_uid

    @property
    def gid(self) -> int:
        """Fetch and return the users group id"""

        return pwd.getpwnam(self._username).pw_gid

    def __str__(self) -> str:
        """Return the parent object's username"""

        return self.username

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.username})'
