Configuration
=============

After installation, the ``notifier`` utility needs to be configured via the application settings file.
Without proper configuration, the application may not work as intended.
At any time, the ``notifier --validate`` command can be run to validate the current application settings.

Email Notification Template
---------------------------

The email message issued to users is customizable via a template file located at ``/etc/notifier/template.html``.
The default template is as follows:

.. literalinclude:: ../../../quota_notifier/data/template.html

Users are encouraged to customize the template to fit their needs.
Automatically formatted fields are indicated using curly braces and are detailed below:

.. csv-table::
   :header: "Template Field", "Summary"

   ``usage_summary``, A plain text table summarizing the user's current storage usage.

Application Settings
--------------------

Application settings are configurable via a settings file at ``/etc/notifier/settings.json``.
If this file does not exist, the application will run using the default settings.
A full list of available settings and their defaults is provided below:


.. important:: The top level ``file_systems`` field is a nested field and entries
   should adhere to the :ref:`#/definitions/FileSystemSchema` schema outlined below.

.. pydantic:: quota_notifier.settings.SettingsSchema

.. _#/definitions/FileSystemSchema:
.. pydantic:: quota_notifier.settings.FileSystemSchema