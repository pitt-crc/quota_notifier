"""Tools for running commands and fetching user data from the underlying system shell."""

from shlex import split
from subprocess import PIPE, Popen


class ShellCmd:
    """Execute commands using the underlying shell

    Outputs to STDOUT and STDERR are exposed via the ``out`` and ``err``
    attributes respectively.
    """

    def __init__(self, cmd: str) -> None:
        """Execute the given command in the underlying shell

        Args:
            cmd: The command to run

        Raises:
            ValueError: When the ``cmd`` argument is empty
        """

        if not cmd:
            raise ValueError('Command string cannot be empty')

        out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()
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

    username: str
    group: str
    uid: int
    gid: int
