Installation
============

Follow the instructions below to install and configure the ``notifier`` utility.

System Utilities
----------------

The ``df`` command line utility must be installed for the quota notifier to
process *generic* file systems. The ``beegfs-ctl`` utility is also required to
support BeeGFS file systems. See :doc:`file_systems` for more details on how
different file system types are expected to be configured.

Installing the Package
----------------------

The ``notifier`` command line utility is installable via the `pip <https://pip.pypa.io/en/stable/>`_
(or `pipx <https://pypa.github.io/pipx/>`_) package manager:

.. code-block::

   pipx install git+https://github.com/pitt-crc/quota_notifier.git

Configuration
-------------

Application settings are configurable via JSON settings file.
The example below includes a minimal subset of useful settings to get up and running.
A full list of available settings is provided in the :doc:`config_options` page.

.. code-block:: json

   {
     "thresholds": [75, 100],
     "blacklist": ["root"],
     "group_blacklist": ["root"],
     "file_systems": [
         {
           "name": "main",
           "path": "/some/filepath",
           "type": "generic"
         }
     ]
   }

By default, the application looks for the settings file at ``/etc/notifier/settings.json``.
This path can also be changed at runtime (see the :doc:`usage` page for more information).

Once the application has been configured, you can check the configuration file is valid by running:

.. code-block:: bash

   notifier --validate

Issuing Automated Notifications
-------------------------------

Email notifications can be automated by scheduling a chron job.
System administrators will want to select a notification frequency that will be useful to users.
Running at least once per day is recommended.

.. code-block::

   0 9 * * 0-6 notifier
