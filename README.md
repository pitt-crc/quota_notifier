# Quota Notification Utility

`notifier` is a command line utility for emailing users when their storage usage on a
monitored file system crosses a configured threshold.

## Requirements

The `df` command line utility must be installed on the host system.

## Installation

Install the package with [pip](https://pip.pypa.io/en/stable/) (or
[pipx](https://pypa.github.io/pipx/)):

```bash
pip install quota-notifier
```

## Quick Start

Application settings are read from `/etc/notifier/settings.json`. If the file does not
exist, the application runs using default settings. The example below is a minimal
configuration that covers most deployments:

```json
{
  "log_path": "/home/notifier.log",
  "log_level": "INFO",
  "db_url": "sqlite:///home/notifier_data.db",
  "uid_blacklist": [
    0
  ],
  "gid_blacklist": [
    0
  ],
  "file_systems": [
    {
      "name": "Example File System",
      "path": "/example",
      "type": "generic",
      "thresholds": [
        50,
        75
      ]
    }
  ],
  "email_from": "no-reply@domain.com",
  "email_domain": "@domain.com",
  "admin_emails": [
    "admin.user@domain.com"
  ]
}
```

Validate the settings file without sending any email:

```bash
notifier --validate
```

Send any pending notifications:

```bash
notifier
```

Notifications are normally automated with a cron job. Running at least once per day is
recommended:

```
0 9 * * 0-6 notifier
```

## Usage

| Command                | Description                                                                                                         |
|------------------------|---------------------------------------------------------------------------------------------------------------------|
| `notifier`             | Send any pending email notifications.                                                                               |
| `notifier --validate`  | Validate the settings file and exit. Exits silently when settings are valid, otherwise prints the invalid settings. |
| `notifier --debug`     | Run without committing to the database or sending email.                                                            |
| `notifier --debug -vv` | Dry run with verbose output, useful for checking which users *would have* been notified.                            |

Run `notifier --help` for the full argument list.

## Configuration

### Core Settings

| Setting            | Default                               | Description                                                                                         |
|--------------------|---------------------------------------|-----------------------------------------------------------------------------------------------------|
| `file_systems`     | `[]`                                  | List of file systems to examine. See [File System Settings](#file-system-settings).                 |
| `uid_blacklist`    | `[0]`                                 | Do not notify users with these UID values.                                                          |
| `gid_blacklist`    | `[0]`                                 | Do not notify groups with these GID values.                                                         |
| `disk_timeout`     | `30`                                  | Give up on checking a file system after this many seconds.                                          |
| `log_level`        | `INFO`                                | Application logging level. One of `DEBUG`, `INFO`, `WARNING`, or `ERROR`.                           |
| `log_path`         |                                       | Optionally log application events to a file.                                                        |
| `smtp_host`        | System default                        | Name of the SMTP host server.                                                                       |
| `smtp_port`        | System default                        | Port for the SMTP server.                                                                           |
| `db_url`           | `sqlite:///notifier_data.db`          | URL for the application database. By default a SQLite database is created in the working directory. |
| `email_from`       | `no-reply@domain.com`                 | From address for automatically generated emails.                                                    |
| `email_subject`    | `CRC Disk Usage Alert`                | Subject line for automatically generated emails.                                                    |
| `email_domain`     | `@domain.com`                         | Appended to usernames when generating email addresses. The leading `@` is optional.                 |
| `admin_emails`     | `[]`                                  | Admin users to contact when the application hits a critical issue.                                  |
| `debug`            | `False`                               | Disable database commits and email notifications. Useful for development and testing.               |

### File System Settings

Each entry in the `file_systems` list requires the following fields:

| Setting      | Description                                                       |
|--------------|-------------------------------------------------------------------|
| `name`       | Human-readable name for the file system.                          |
| `path`       | Absolute path to the mounted file system.                         |
| `type`       | File system type. One of `ihome`, `generic`, `beegfs`, or `vast`. |
| `thresholds` | Usage percentages to issue notifications for.                     |

Adding a new file system type also requires updating `QuotaType` in
`quota_notifier.disk_utils.QuotaFactory`.

### Blacklisting Users and Groups

The `uid_blacklist` and `gid_blacklist` options accept individual ID values and
inclusive ID ranges. To ignore the `root` user in addition to users `100` through `199`:

```json
{
  "uid_blacklist": [
    0,
    [
      100,
      199
    ]
  ]
}
```

The default value for both options is `[0]`, which excludes the `root` user and group.

### Email Template

The email sent to users is rendered from an HTML template at
`/etc/notifier/template.html`, which is intended to be customized. Formatted fields are
indicated with curly braces:

| Template Field  | Description                                                      |
|-----------------|------------------------------------------------------------------|
| `usage_summary` | A plain text table summarizing the user's current storage usage. |

## Supported File Systems

Most file systems are supported by default, with dedicated support for the types below.

**Generic** — Any file system where usage and available space can be determined with
`os.statvfs`. Generic file systems **must** be organized so that each subdirectory is
named after a user group. For a file system mounted at `/mnt`, the directory for group
`group1` must be `/mnt/group1`. Directories not named after a user group are ignored,
and a directory does not have to exist for every group.

**BeeGFS** — Quota information is read directly from the `beegfs-ctl` utility, so there
are no requirements on how the file system is organized.

**ihome** — Usage is determined with `os.statvfs` against the user's home directory.
Since VAST reports the quota limit as the size of the underlying file system when no
quota is configured, a user is skipped if their reported size is within 1% of the
enclosing mount point's size.

**vast** — Usage is determined the same way as **ihome**, but against a group directory
on VAST-hosted storage (organized the same way as **generic** file systems).
