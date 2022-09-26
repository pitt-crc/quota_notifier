Installation
============

The ``notifier`` command line utility is installable via the `pip <https://pip.pypa.io/en/stable/>`_
(or `pipx <https://pypa.github.io/pipx/>`_) package manager:

.. code-block::

   pipx install git+https://github.com/pitt-crc/quota_notifier.git

If you are working as a developer, installation options are provided for extra dependencies:

.. code-block:: bash

    git clone https://github.com/pitt-crc/quota_notifier
    pip install quota_notifier.[all]

To install a specific subset of extras, chose from the options below.
All options will install the ``notifier`` utility plus core package dependencies.

+----------------------+---------------------------------------------------------+
| Install Option       | Description                                             |
+======================+=========================================================+
| ``[all]``            | Install all extra dependencies listed in this table.    |
+----------------------+---------------------------------------------------------+
| ``[docs]``           | Dependencies required for building the documentation.   |
+----------------------+---------------------------------------------------------+
| ``[tests]``          | Dependencies required for running tests with coverage.  |
+----------------------+---------------------------------------------------------+

Configuration
-------------

Application settings are configurable via JSON settings file.
The example below includes a minimal subset of useful settings to get up and running.
A full list of available settings is provided in the :doc:`settings` page.

.. code-block:: json

   {
     "thresholds": [75, 100],
     "file_systems": null,
     "blacklist": null,
   }

By default, the application looks for the settings file at ``/etc/notifier/settings.json``.
This path can also be changed at runtime (see the :doc:`usage` page for more information).

Once the application has been configured, you can check the configuration file is valid by running:

.. code-block:: bash

   notifier check

Issuing Automated Notifications
-------------------------------

Email notifications can be automated by scheduling a chron job.
System administrators will want to select a notification frequency that will be useful to users.
Running at least once per day is recommended.

.. code-block::

   0 9 * * 0-6 notifier notify
