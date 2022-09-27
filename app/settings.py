"""The ``settings`` module is responsible for managing application settings.
Class definitions directly reflect the settings file schema.

Module Contents
---------------
"""

from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field, validator

DEFAULT_DB_PATH = Path(__file__).parent.resolve() / 'app_data.db'


class FileSystemSchema(BaseSettings):
    """Defines the schema settings related to an individual file system"""

    name: str = Field(
        ...,
        title='System Name',
        type=str,
        description='Human readable name for the file system')

    path: Path = Field(
        ...,
        title='System Path',
        type=Path,
        description='Absolute path to the mounted file system')

    type: str = Field(
        ...,
        title='System Type',
        type=str,
        description='Type of the file system')

    @validator('type')
    def validate_type(cls, value: str) -> str:
        """Ensure the given system type is a valid quota object

        Args:
            value: The value to validate

        Returns:
            The validated file system type
        """

        from .disk_utils import QuotaFactory

        valid_types = list(QuotaFactory.quota_types.keys())
        if value not in valid_types:
            raise ValueError(f'File system types must be one of {valid_types}')

        return value

    @validator('path')
    def validate_path(cls, value: Path) -> Path:
        """Ensure the given system path exists

        Args:
            value: The path value to validate

        Returns:
            The validated system path
        """

        if not value.exists():
            raise ValueError(f'File system does not exist {value}')

        return value


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

    # Settings for the smtp port
    smtp_server: str = Field(
        title='SMTP Server Host Name',
        type=str,
        default='localhost',
        description='Name of the remote SMTP host'
    )

    smtp_port: int = Field(
        title='SMTP Port Number',
        type=int,
        default=0,
        description='Port for the SMTP server'
    )

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

    email_domain: str = Field(
        title='User Email Address Domain',
        type=str,
        default='@pitt.edu',
        description=('String to append to usernames when generating user email addresses. '
                     'The leading `@` is optional.'))

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

    @validator('file_systems')
    def validate_unique_file_systems(cls, value: list[FileSystemSchema]) -> list[FileSystemSchema]:
        """Ensure file systems have unique names/paths

        Args:
            value: The file systems to validate

        Returns:
            The validated file systems
        """

        paths = [fs.path for fs in value]
        if len(set(paths)) != len(paths):
            raise ValueError('File systems do not have unique paths')

        names = [fs.name for fs in value]
        if len(set(names)) != len(names):
            raise ValueError('File systems do not have unique names')

        return value


class ApplicationSettings:
    """Configurable application settings object

    Application settings can be fetched but not set from the class instance.
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
