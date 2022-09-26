"""The ``settings`` module is responsible for managing application settings.
Class definitions directly reflect the settings file schema.

Module Contents
---------------
"""

from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field

DEFAULT_DB_PATH = Path(__file__).parent.resolve() / 'app_data.db'


class FileSystemSchema(BaseSettings):
    """Defines the schema settings related to an individual file system"""

    name: str = Field(
        ...,
        title='System Name',
        type=str,
        description='Human readable name for the file system')

    path: str = Field(
        ...,
        title='System Path',
        type=str,
        description='Absolute path to the mounted file system')

    type: str = Field(
        ...,
        title='System Type',
        type=str,
        description='Type of the file system')


class SettingsSchema(BaseSettings):
    """Defines the schema and default values for top level application settings"""

    ihome_quota_path: Path = Field(
        title='Ihome Quota Path',
        type=Path,
        default=Path('/ihome/crc/scripts/ihome_quota.json'),
        description='Path to ihome storage information.')

    thresholds: list[int] = Field(
        title='Notification Thresholds',
        type=list[int],
        default=[98, 100],
        description='Usage percentages to issue notifications for.')

    file_systems: list[FileSystemSchema] = Field(
        title='Monitored File Systems',
        type=list[FileSystemSchema],
        default=list(),
        description='List of additional settings that define which file systems to examine.')

    blacklist: set[str] = Field(
        title='Blacklisted Users',
        type=set[str],
        default=set(),
        description='Do not notify usernames in this list.')

    disk_timeout: int = Field(
        title='File System Timeout',
        type=int,
        default=30,
        description='Give up on checking a file system after the given number of seconds.')

    # Settings for database connections
    db_url: str = Field(
        title='Database Path',
        type=str,
        default=f'sqlite:///{DEFAULT_DB_PATH}',
        description=('Path to the application database. '
                     'Default value varies by installed system but is always in the installation directory.'))

    # Email notification settings
    email_from: str = Field(
        title='Email From Address',
        type=str,
        default='no-reply@crc.pitt.edu',
        description='From address for automatically generated emails.')

    email_subject: str = Field(
        title='Email Subject Line',
        type=str,
        default='CRC Disk Usage Alert',
        description='Subject line for automatically generated emails.')

    email_header: str = Field(
        title='Email Header Text',
        type=str,
        description='Opening email paragraph(s) displayed before the automated quota summary.',
        default=("This is an automated notification concerning your storage quota on H2P. "
                 "One or more of your quotas have surpassed a usage threshold triggering an automated notification. "
                 "Your storage usage is as follows:"))

    email_footer: str = Field(
        title='Email Footer Text',
        type=str,
        description='Ending email paragraph(s) displayed after the automated quota summary.',
        default=(
            "If you need additional storage, please submit a request via the CRC ticketing system. "
            "Our storage policies are described in https://crc.pitt.edu/user-support/data-storage-guidelines.\n\n"
            "Sincerely,\n"
            "The CRC Quota Bot"
        ))


class ApplicationSettings:
    """Configurable application settings object

    Application settings can be fetched (but not set) from the class instance
    via dictionary style indexing.

    Use the ``configure_from_file`` method to load settings from a settings file.
    """

    _parsed_settings: SettingsSchema = SettingsSchema()

    @classmethod
    def configure_from_file(cls, path: Path) -> None:
        """Update application settings using values from a given file path

        Args:
            path: Path to load settings from
        """

        cls._parsed_settings = SettingsSchema.parse_file(path)

    @classmethod
    def get(cls, item: str) -> Any:
        """Return a value from application settings

        Args:
            item: The name of the settings value to retrieve
        """

        return getattr(cls._parsed_settings, item)
