"""The ``settings`` module is responsible for managing application settings.
Class definitions directly reflect the settings file schema.

Module Contents
---------------
"""

import logging
from pathlib import Path
from typing import Any, List, Set
from typing import Literal

from pydantic import BaseSettings, Field, validator

from quota_notifier.orm import DBConnection

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

    # If modifying options for this setting, also update
    # quota_notifier.disk_utils.QuotaFactory.QuotaType
    type: Literal['ihome', 'generic', 'beegfs'] = Field(
        ...,
        title='System Type',
        type=Literal['ihome', 'generic', 'beegfs'],
        description='Type of the file system')

    @validator('name')
    def validate_name(cls, value: str) -> str:
        """Ensure the given name is not blank

        Args:
            value: The name value to validate

        Returns:
            The validated file system name
        """

        if not value.strip():
            raise ValueError(f'File system name cannot be blank')

        return value

    @validator('path')
    def validate_path(cls, value: Path) -> Path:
        """Ensure the given system path exists

        Args:
            value: The path value to validate

        Returns:
            The validated path object

        Raises:
            ValueError: If the path does not exist
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

    thresholds: List[int] = Field(
        title='Notification Thresholds',
        type=List[int],
        default=[98, 100],
        description='Usage percentages to issue notifications for.')

    file_systems: List[FileSystemSchema] = Field(
        title='Monitored File Systems',
        type=List[FileSystemSchema],
        default=list(),
        description='List of additional settings that define which file systems to examine.')

    blacklist: Set[str] = Field(
        title='Blacklisted Users',
        type=Set[str],
        default={'root', },
        description='Do not notify usernames in this list.')

    group_blacklist: Set[str] = Field(
        title='Blacklisted Groups',
        type=Set[str],
        default={'root', },
        description='Do not notify groups in this list.')

    disk_timeout: int = Field(
        title='File System Timeout',
        type=int,
        default=30,
        description='Give up on checking a file system after the given number of seconds.')

    # Settings for the smtp host/port
    smtp_host: str = Field(
        title='SMTP Server Host Name',
        type=str,
        default='',
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

    debug: bool = Field(
        title='Debug Mode',
        type=bool,
        default=False,
        description='Disable database commits and email notifications. Useful for development and testing.')

    @validator('file_systems')
    def validate_unique_file_systems(cls, value: List[FileSystemSchema]) -> List[FileSystemSchema]:
        """Ensure file systems have unique names/paths

        Args:
            value: The file systems to validate

        Returns:
            The validated file systems

        Raises:
            ValueError: If the file system names and paths are not unique
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

    Use the ``configure`` method to override individual default settings.
    Use the ``configure_from_file`` method to load settings from a settings file.
    """

    _parsed_settings: SettingsSchema = SettingsSchema()

    @classmethod
    def _configure_logging(cls, level: int) -> None:
        """Configure python logging to the given level

        Arguments for the ``level`` argument are NOT the same as the
        default integer values used by Python to enumerate logging levels.
        Accepted values are 0 (no logging information displayed),
        1 (information level logging) and 2 (debug level logging).

        Args:
            level: Integer representing the desired logging level.
        """

        log_format = '%(levelname)8s - %(message)s'
        if level == 0:
            logging.basicConfig(level=100, format=log_format)

        elif level == 1:
            logging.basicConfig(level=logging.WARNING, format=log_format)

        elif level == 2:
            logging.basicConfig(level=logging.INFO, format=log_format)

        else:
            logging.basicConfig(level=logging.DEBUG, format=log_format)

    @classmethod
    def _configure_database(cls) -> None:
        """Configure the application database connection"""

        if cls.get('debug'):
            logging.warning('Running in debug mode')
            DBConnection.configure('sqlite:///:memory:')

        else:
            DBConnection.configure(cls.get('db_url'))

    @classmethod
    def _configure(cls):
        """Update backend application constructs to reflect current application settings"""

        cls._configure_logging(1)
        cls._configure_database()

    @classmethod
    def set_from_file(cls, path: Path) -> None:
        """Reset application settings to default values

        Values defined in the given file path are used to override defaults.

        Args:
            path: Path to load settings from
        """

        logging.debug(f'Looking for settings file: {path.resolve()}')

        try:
            cls._parsed_settings = SettingsSchema.parse_file(path)
            cls._configure()

        except Exception:
            logging.error('settings file is invalid')
            raise

        logging.info(f'Loaded settings from file: {path.resolve()}')

    @classmethod
    def set(cls, **kwargs) -> None:
        """Update values in the application settings

        Unlike the ``configure`` and ``configure_from_file`` methods,
        application settings not specified as keyword arguments are left
        unchanged.

        Raises:
            ValueError: If the item name is not a valid setting
        """

        for item, value in kwargs.items():
            if not hasattr(cls._parsed_settings, item):
                ValueError(f'Invalid settings option: {item}')

            setattr(cls._parsed_settings, item, value)

        cls._configure()

    @classmethod
    def reset_defaults(cls) -> None:
        """Reset application settings to default values"""

        cls._parsed_settings = SettingsSchema()

    @classmethod
    def get(cls, item: str) -> Any:
        """Return a value from application settings

        Args:
            item: Name of the settings value to retrieve

        Returns
           The value currently configured in application settings
        """

        return getattr(cls._parsed_settings, item)
