Usage Example
=============

To send any pending email notifications, call ``notifier`` utility:

.. code-block:: bash

   notifier


By default, the application looks for application settings at ``/etc/notifier/settings.json``.
This path can be customized via the ``-s`` argument:

.. code-block::

      notifier -s [SETTINGS-PATH]

The ``notifier`` utility will automatically validate the application settings file before issuing email notifications.
However, the settings file can be validated without issuing email notifications by running:

.. code-block:: bash

   notifier --check

Full documentation for the commandline interface is provided below.

Commandline Interface
---------------------

.. argparse::
   :ref: app.cli.Parser
   :prog: notifier

