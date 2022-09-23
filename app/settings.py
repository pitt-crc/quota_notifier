"""The ``settings`` module is responsible for managing application settings.
Class definitions directly reflect the settings file schema.

Module Contents
---------------
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseSettings

SETTINGS_PATH = Path('/etc/notifier/config.json')
DEFAULT_DB_PATH = Path(__file__).parent.resolve() / 'app_data.db'


class FileSystem(BaseSettings):
    """Settings for an individual file system"""

    name: str
    path: str
    type: str


class Settings(BaseSettings):
    """Top level settings object for the parent application"""

    ihome_quota_path: Path = Path('/ihome/crc/scripts/ihome_quota.json')
    thresholds: tuple[int, ...] = (75, 100)
    file_systems: Optional[tuple[FileSystem, ...]]
    blacklist: Optional[set[str]]
    disk_timeout: int = 30

    # Settings for database connections
    db_url: str = f'sqlite:///{DEFAULT_DB_PATH}'

    # Email notification settings
    email_from: str = 'no-reply@crc.pitt.edu'
    email_subject: str = 'CRC Disk Usage Alert'
    email_header = (
        "This is an automated notification concerning your storage quota on H2P. "
        "One or more of your quotas have surpassed a usage threshold triggering an automated notification. "
        "Your storage usage is as follows:")

    email_footer = (
        "If you need additional storage, please submit a request via the CRC ticketing system. "
        "Our storage policies are described in https://crc.pitt.edu/user-support/data-storage-guidelines.\n\n"
        "Sincerely,\n"
        "The CRC Quota Bot"
    )


if SETTINGS_PATH.exists():
    app_settings = Settings.parse_file(SETTINGS_PATH)

else:
    app_settings = Settings()
