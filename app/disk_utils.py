"""Utilities for fetching disk quota information."""

from __future__ import annotations

import math


class AbstractQuota(object):
    """Base class for building object-oriented representations of file system quotas."""

    def __init__(self, name: str, size_used: int, size_limit: int) -> None:
        """Create a new quota from known system metrics

        Args:
            name: Human readable name of the file system
            size_used: Disk space used by the user/group
            size_limit: Maximum disk space allowed by the allocation
        """

        self.name = name
        self.size_used = size_used
        self.size_limit = size_limit

    def __str__(self) -> str:
        used_str = self.bytes_to_str(self.size_used)
        limit_str = self.bytes_to_str(self.size_limit)
        percentage = (self.size_used * 100) // self.size_limit
        return f"{self.name}: {used_str} / {limit_str} ({percentage}%)"

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
