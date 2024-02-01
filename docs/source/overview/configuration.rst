Configuration
=============

After installation, the ``notifier`` utility needs to be configured via the application settings file.
Instructions for customizing the application are provided below.
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
A full list of available settings and their defaults is provided below.


Core Settings
.............

.. important:: The top level ``file_systems`` field is a nested field and entries
   should adhere to the :ref:`fs-label` schema outlined below.

+------------------+-----------------------------------------+---------------------------------------------------------+
| Setting          | Default Value                           | Description                                             |
+==================+=========================================+=========================================================+
| ihome_quota_path | ``/ihome/crc/scripts/ihome_quota.json`` | Path to ihome storage information.                      |
+------------------+-----------------------------------------+---------------------------------------------------------+
| file_systems     | ``[]``                                  | List of file systems to examine. See the                |
|                  |                                         | :ref:`fs-label` section for details                     |
+------------------+-----------------------------------------+---------------------------------------------------------+
| uid_blacklist    | ``[0]``                                 | Do not notify users with these UID values.              |
+------------------+-----------------------------------------+---------------------------------------------------------+
| gid_blacklist    | ``[0]``                                 | Do not notify groups with these GID values.             |
+------------------+-----------------------------------------+---------------------------------------------------------+
| disk_timeout     | ``30``                                  | Give up on checking a file system after                 |
|                  |                                         | the given number of seconds.                            |
+------------------+-----------------------------------------+---------------------------------------------------------+
| log_level        | ``INFO``                                | Application logging level.                              |
| log_level        | ``INFO``                                | One of ``DEBUG``, ``INFO``, ``WARNING``, or ``ERROR``.  |
+------------------+-----------------------------------------+---------------------------------------------------------+
| log_path         |                                         | Optionally log application events to a                  |
|                  |                                         | file.                                                   |
+------------------+-----------------------------------------+---------------------------------------------------------+
| smtp_host        | Matches system default.                 | Name of the SMTP host server.                           |
+------------------+-----------------------------------------+---------------------------------------------------------+
| smtp_port        | Matches system default.                 | Port for the SMTP server.                               |
+------------------+-----------------------------------------+---------------------------------------------------------+
| db_url           | ``sqlite:///notifier_data.db``          | URL for the application database. By                    |
|                  |                                         | default, a SQLITE database is created in                |
|                  |                                         | the working directory.                                  |
+------------------+-----------------------------------------+---------------------------------------------------------+
| email_from       | ``no-reply@domain.com``                 | From address for automatically generated                |
|                  |                                         | emails.                                                 |
+------------------+-----------------------------------------+---------------------------------------------------------+
| email_subject    | ``CRC Disk Usage Alert``                | Subject line for automatically generated                |
|                  |                                         | emails.                                                 |
+------------------+-----------------------------------------+---------------------------------------------------------+
| email_domain     | ``@domain.com``                         | String to append to usernames when                      |
|                  |                                         | generating user email addresses. The                    |
|                  |                                         | leading ``@`` is optional.                              |
+------------------+-----------------------------------------+---------------------------------------------------------+
| admin_emails     | ``[]``                                  | Admin users to contact when the                         |
|                  |                                         | application encounters a critical issue.                |
+------------------+-----------------------------------------+---------------------------------------------------------+
| debug            | ``False``                               | Disable database commits and email                      |
|                  |                                         | notifications. Useful for development                   |
|                  |                                         | and testing.                                            |
+------------------+-----------------------------------------+---------------------------------------------------------+

.. _fs-label:

File System Settings
....................

The following fields are required when defining which file systems to scan.

+------------------------+---------------------------------------------------------------------------------------------+
| Setting                | Description                                                                                 |
+========================+=============================================================================================+
| name                   | Human-readable name for the file system.                                                    |
+------------------------+---------------------------------------------------------------------------------------------+
| path                   | Absolute path to the mounted file system.                                                   |
+------------------------+---------------------------------------------------------------------------------------------+
| type                   | Type of the file system. Options: ``ihome``, ``generic``, ``beegfs``. If modifying options, |
|                        | update QuotaType in ``quota_notifier.disk_utils.QuotaFactory``.                             |
+------------------------+---------------------------------------------------------------------------------------------+
| thresholds             | Usage percentages to issue notifications for.                                               |
+------------------------+---------------------------------------------------------------------------------------------+

