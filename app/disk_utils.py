"""Utilities for fetching disk quota information.

Different quota objects (classes) are provided for different file system structures.
The ``GenericQuota`` is generally applicable to any file system whose
quota can be determined using the ``df`` commandline utility.

Quota classes may provide factory methods to facilitate creating instances
based on simple user data. In all cases, these methods will return ``None``
if a quota is not found for the user.

Using ``QuotaFactory`` class is recommended when dynamically creating quota
objects for varying paths, users, or filesystem types.

Module Contents
---------------
"""

from __future__ import annotations

import json
import math
from abc import abstractmethod
from pathlib import Path
from typing import Optional

from .settings import app_settings
from .shell import ShellCmd, User


class AbstractQuota(object):
    """Base class for building object-oriented representations of file system quotas."""

    def __init__(self, name: str, user: User, size_used: int, size_limit: int) -> None:
        """Create a new quota from known system metrics

        Args:
            name: Human readable name of the file system
            user: User that the quota is tied to
            size_used: Disk space used by the user/group
            size_limit: Maximum disk space allowed by the allocation
        """

        self.name = name
        self.user = user
        self.size_used = size_used
        self.size_limit = size_limit

    @classmethod
    @abstractmethod
    def get_quota(cls, name: str, path: Path, user: User) -> Optional[AbstractQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Returns:
            An instance of the parent class or None if the allocation does not exist
        """

    @staticmethod
    def bytes_to_str(size: int) -> str:
        """Convert the given number of bytes to a human-readable string

        Args:
            size: An integer number of bytes

        Returns:
             A string representation of the given size with units
        """

        if size == 0:
            return '0.0 B'

        size_units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

        base_2_power = int(math.floor(math.log(size, 1024)))
        conversion_factor = math.pow(1024, base_2_power)
        final_size = round(size / conversion_factor, 2)
        return f'{final_size} {size_units[base_2_power]}'

    def __str__(self) -> str:
        used_str = self.bytes_to_str(self.size_used)
        limit_str = self.bytes_to_str(self.size_limit)
        percentage = (self.size_used * 100) // self.size_limit
        return f"{self.name}: {used_str} / {limit_str} ({percentage}%)"


class GenericQuota(AbstractQuota):
    """The default quota object for most file system types"""

    @classmethod
    def get_quota(cls, name: str, path: Path, user: User) -> Optional[GenericQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Returns:
            An instance of the parent class or None if the allocation does not exist
        """

        df_command = f"df {path}"
        quota_info_list = ShellCmd(df_command).out.splitlines()
        if not quota_info_list:
            return None

        result = quota_info_list[1].split()
        return cls(name, user, int(result[2]) * 1024, int(result[1]) * 1024)


class BeegfsQuota(AbstractQuota):
    """Disk storage quota for a BeeGFS file system"""

    @classmethod
    def get_quota(cls, name: str, path: Path, user: User, storage_pool: int = 1) -> Optional[BeegfsQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to
            storage_pool: Beegfs storagepoolid to create a quota for

        Returns:
            An instance of the parent class or None if the allocation does not exist
        """

        quota_info_cmd = ShellCmd(f"beegfs-ctl --getquota --gid {user.group} --csv --storagepoolid={storage_pool}")
        if quota_info_cmd.err:
            return None

        result = quota_info_cmd.out.splitlines()[1].split(',')
        return cls(name, user, int(result[2]), int(result[3]))


class IhomeQuota(AbstractQuota):
    """Disk storage quota for the ihome file system"""

    @classmethod
    def get_quota(cls, name: str, path: Path, user: User) -> Optional[IhomeQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Returns:
            An instance of the parent class or None if the allocation does not exist
        """

        # Get the information from Isilon
        with app_settings.ihome_quota_path.open('r') as infile:
            data = json.load(infile)

        persona = f"UID:{user.uid}"
        for item in data["quotas"]:
            if item["persona"] is not None:
                if item["persona"]["id"] == persona:
                    return cls(name, user, item["usage"]["logical"], item["thresholds"]["hard"])


class QuotaFactory:
    """Factory object for dynamically creating quota instances of different types"""

    quota_types = dict(
        generic=GenericQuota,
        beegfs=BeegfsQuota,
        ihome=IhomeQuota
    )

    def __new__(cls, quota_type: str, name: str, path: Path, user: User, **kwargs) -> AbstractQuota:
        """Create a new quota instance

        See the ``quota_types`` attribute for valid values to the ``quota_type`` argument.

        Args:
            quota_type: String representation of the return type object
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Return:
              A quota instance of the specified type created using the given arguments
        """

        if quota_type not in cls.quota_types:
            raise ValueError(f'Unknown quota type {quota_type}')

        return cls.quota_types[quota_type](name, path, user, **kwargs)
