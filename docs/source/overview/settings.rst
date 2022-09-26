Config Options
==============

The ``SettingsSchema`` defines the available options in the application settings file.
Note the ``file_systems`` field is a nested field and should adhere to the ``FileSystemSchema`` schema.

.. pydantic:: app.settings.SettingsSchema

.. _#/definitions/FileSystemSchema:
.. pydantic:: app.settings.FileSystemSchema