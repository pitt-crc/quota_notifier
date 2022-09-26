Config Options
==============

The ``SettingsSchema`` defines the available options in the application settings file.

.. pydantic:: app.settings.SettingsSchema

Entries for the ``file_systems`` field should adhere to the ``FileSystemSchema`` schema.

.. pydantic:: app.settings.FileSystemSchema