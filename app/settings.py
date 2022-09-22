"""The ``settings`` module is responsible for managing application settings.
Class definitions directly reflect the settings file schema.

Module Contents
---------------
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseSettings

path = Path(__file__).parent / 'app_data.db'


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

    # Ldap settings
    # Authentication values default to anonymous session
    ldap_server: str = 'pittad.univ.pitt.edu'
    ldap_port: int = 389
    ldap_user: Optional[str] = None
    ldap_password: Optional[str] = None

    # Settings for database connections
    db_url: str = f'sqlite:///{path.resolve()}'


app_settings = Settings()
