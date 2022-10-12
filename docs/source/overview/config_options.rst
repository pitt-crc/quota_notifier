Config Options
==============

The ``SettingsSchema`` defines the available options in the application settings file.
Note the ``file_systems`` field is a nested field and should adhere to the ``FileSystemSchema`` schema.

.. pydantic:: quota_notifier.settings.SettingsSchema

.. _#/definitions/FileSystemSchema:
.. pydantic:: quota_notifier.settings.FileSystemSchema