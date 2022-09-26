Usage Example
=============

The ``notifier`` utility will automatically validate the application settings file before issuing email notifications.
However, the settings file can also be validated at will by running:

.. code-block:: bash

   notifier -c [SETTINGS-PATH] check

If the setting file path is not provided, the system defaults to the path ``/etc/notifier/settings.json``.

To send any pending email notifications, use the ``notify`` command:

.. code-block:: bash

   notifier -c [SETTINGS-PATH] notify

Full documentation for the commandline interface is provided below.

Commandline Interface
---------------------

.. argparse::
   :ref: app.cli.Parser
   :prog: notifier

