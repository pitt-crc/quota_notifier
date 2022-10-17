Supported File Systems
======================

The quota notification utility supports most file systems by default.
However, dedicated support is provided for specific file system types.
Different file systems may have requirements on their setup/organization.

Generic File Systems
--------------------

Most file systems are supported as *generic* file systems.
This includes any system where the current usage and available space can be determined via the ``df`` utility.
Generic file systems **must** be organized such that each subdirectory is named after a user group.
For example, if the file system is mounted at ``/mnt``, the directory for user group ``group1`` should be ``/mnt/gropup1``.

Directories not named after a user group are ignored. A directory does not have to exist for every group.

BeeGFS Systems
--------------

Dedicated support is provided for BeeGFS file systems.
Unlike generic file systems, there are no requirements on how the Beegfs system is organized.
Quota information is fetched directly from the ``beegfs-ctl`` utility.
