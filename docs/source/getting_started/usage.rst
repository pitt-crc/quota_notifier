Usage Examples
==============

Simple usage examples are provided below for the ``notifier`` commandline utility.
Full documentation for the commandline interface is available in the :doc:`command_line` page.

Blacklist Users and Groups
--------------------------

Individual users and groups can be blacklisted from recieving notifications using their system ID values.
In the application settings file (located at ``/etc/notifier/settings.json`` by default) specify the
``uid_blacklist`` and ``gid_blacklist`` options to blacklist users/groups:

.. code-block:: json

   {
     "uid_blacklist": [0, 4, 7],
     "gid_blacklist": [0, 1, 5],
   }

The ``uid_blacklist`` and ``gid_blacklist`` fields also accept ID ranges.
For example, to ignore the ``root`` user in addition to users ``100`` through ``199``:

.. code-block:: json

   {
     "uid_blacklist": [0, [100, 199]]
   }

All ID ranges are treated as being inclusive.

.. note:: The default value for the ``uid_blacklist`` and ``gid_blacklist`` options is ``[0]`` which excludes
          the ``root`` user/group.

Validate Application Settings
-----------------------------

By default, the application looks for application settings at ``/etc/notifier/settings.json``.
This path can be customized via the ``-s`` argument:

.. code-block::

      notifier -s [SETTINGS-PATH]

The ``notifier`` utility will automatically validate the application settings file before issuing email notifications.
However, the settings file can be validated without issuing email notifications by setting the ``--validate`` flag:

.. code-block:: bash

   notifier -s [SETTINGS-PATH] --validate

If the settings are valid, the application will exit silently.
Otherwise, an error message will detail the invalid settings.

Execute A Dry Run
-----------------

Specifying the ``--debug`` argument will run the application without issuing any email notifications.
It is particularly useful when combined with the verbosity argument for tracking which users **would have** received
notifications (among other runtime information).

.. code-block:: bash

   notifier --debug -vv

Send Pending Notifications
--------------------------

To send any pending email notifications, call the ``notifier`` utility without any arguments:

.. code-block:: bash

   notifier

If running the application on an automatic schedule, you may find it useful to increase the verbosity and write
the application output to a system log:

.. code-block:: bash

   notifier -vv >> notifier.log 2>&1
