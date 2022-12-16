Config Options
==============

The ``SettingsSchema`` defines the available options in the application settings file.

.. important:: The top level ``file_systems`` field is a nested field and entries
   should adhere to the :ref:`#/definitions/FileSystemSchema` schema outlined below.

.. note:: If the SMTP host is ``''`` and the SMTP port is ``0``, the default OS behavior
   will be used for connecting to the SMTP server.

.. pydantic:: quota_notifier.settings.SettingsSchema

.. _#/definitions/FileSystemSchema:
.. pydantic:: quota_notifier.settings.FileSystemSchema