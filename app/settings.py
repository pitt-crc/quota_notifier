"""Load and manage settings for the parent application"""

from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


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

    # Email notification settings
    email_from: str = 'no-reply@crc.pitt.edu'
    email_subject: str = "CRC Disk Usage Update"
    email_header = "This is an email header"
    email_footer = "This is a footer"


app_settings = Settings()
