"""The ``settings`` module is responsible for managing application settings.
Class definitions directly reflect the settings file schema.

Module Contents
---------------
"""

import logging
from pathlib import Path
from typing import Any, List, Union, Tuple, Set, Optional, Literal

from pydantic import BaseSettings, Field, validator

from quota_notifier.logging import ApplicationLog
from quota_notifier.orm import DBConnection

DEFAULT_DB_PATH = Path.cwd().resolve() / 'notifier_data.db'


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

    thresholds: List[int] = Field(
        title='Notification Thresholds',
        type=List[int],
        description='Usage percentages to issue notifications for.')

    @validator('name')
    def validate_name(cls, value: str) -> str:
        """Ensure the given name is not blank

        Args:
            value: The name value to validate

        Returns:
            The validated file system name
        """

        stripped = value.strip()
        if not stripped:
            raise ValueError(f'File system name cannot be blank')

        return stripped

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
            raise ValueError(f'File system path does not exist {value}')

        return value

    @validator('thresholds')
    def validate_thresholds(cls, value: list) -> list:
        """Validate threshold values are between 0 and 100 (exclusive)

        Args:
            value: List of threshold values to validate

        Returns:
            The validated threshold values
        """

        if not value:
            raise ValueError(f'At least one threshold must be specified per file system')

        for threshold in value:
            if not 100 > threshold > 0:
                raise ValueError(f'Notification threshold {threshold} must be greater than 0 and less than 100')

        return value


class SettingsSchema(BaseSettings):
    """Defines the schema and default values for top level application settings"""

    # General application settings
    ihome_quota_path: Path = Field(
        title='Ihome Quota Path',
        type=Path,
        default=Path('/ihome/crc/scripts/ihome_quota.json'),
        description='Path to ihome storage information.')

    file_systems: List[FileSystemSchema] = Field(
        title='Monitored File Systems',
        type=List[FileSystemSchema],
        default=list(),
        description='List of additional settings that define which file systems to examine.')

    uid_blacklist: Set[Union[int, Tuple[int, int]]] = Field(
        title='Blacklisted User IDs',
        type=Set[Union[int, Tuple[int, int]]],
        default=[0],
        description='Do not notify users with these ID values.')

    gid_blacklist: Set[Union[int, Tuple[int, int]]] = Field(
        title='Blacklisted Group IDs',
        type=Set[Union[int, Tuple[int, int]]],
        default=[0],
        description='Do not notify groups with these ID values.')

    disk_timeout: int = Field(
        title='File System Timeout',
        type=int,
        default=30,
        description='Give up on checking a file system after the given number of seconds.')

    # Settings for application logging
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = Field(
        title='Logging Level',
        type=Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        description='Application logging level.')

    log_path: Optional[Path] = Field(
        title='Log Path',
        type=Optional[Path],
        default=None,
        description='Optionally log application events to a file.')

    # Settings for the smtp host/port
    smtp_host: str = Field(
        title='SMTP Server Host Name',
        type=str,
        default='',
        description='Name of the SMTP host server'
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
        description=('URL for the application database. '
                     'By default, a SQLITE database is created in the working directory.'))

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

    # Settings for debug / dry-runs
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

    _parsed_settings: SettingsSchema = None

    @classmethod
    def _configure_logging(cls) -> None:
        """Configure python logging to the given level"""

        log_path = cls.get('log_path')
        log_level = cls.get('log_level')
        if log_path is not None:
            ApplicationLog.configure_log_file(log_level, log_path)

    @classmethod
    def _configure_database(cls) -> None:
        """Configure the application database connection"""

        if cls.get('debug'):
            logging.warning('Running in debug mode')
            DBConnection.configure('sqlite:///:memory:')

        else:
            DBConnection.configure(cls.get('db_url'))

    @classmethod
    def _configure_application(cls):
        """Update backend application constructs to reflect current application settings"""

        cls._configure_logging()
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
            cls._configure_application()

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

        cls._configure_application()

    @classmethod
    def reset_defaults(cls) -> None:
        """Reset application settings to default values"""

        cls._parsed_settings = SettingsSchema()
        cls._configure_application()

    @classmethod
    def get(cls, item: str) -> Any:
        """Return a value from application settings

        Args:
            item: Name of the settings value to retrieve

        Returns
           The value currently configured in application settings
        """

        return getattr(cls._parsed_settings, item)
