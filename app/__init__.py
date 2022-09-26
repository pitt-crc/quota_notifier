"""A simple command line application for notifying users when their storage
quota exceeds a certain percentage.

Overview
--------

Multitenant computing environments commonly enforce user/group limits on
shared storage resources. Enforcing storage quotas ensures resources
are shared fairly among users and is often necessary for establishing
broader system policies. However, quota enforcement can also come as a
hindrance to users when not implemented in a clear, accessible way.

When implementing any kind of resource limit, it is important for users to
have a means to check their overall usage. In addition to providing passive
monitoring, where the user is required to self-initialize an action to
determine their quota status, it is important to actively notify users
when a quota is nearing exhaustion. Doing so helps ensure users are making
responsible decisions concerning their allocation and reduces

The Quota Notification Utility automatically scans attached file systems and
issues email notifications to users exceeding a certain percentage of their
storage quota. The tool is easily configurable and supports multiple file
system types and various notification settings.
"""

__version__ = '0.0.1'
__author__ = 'Pitt Center for Research Computing'
__license__ = 'All rights reserved'
