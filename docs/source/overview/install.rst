Installation
============

The command line applications are installable as a collective set via the
`pip <https://pip.pypa.io/en/stable/>`_ (for local installs) or
`pipx <https://pypa.github.io/pipx/>`_ (for system wide installs)
package managers:

.. code-block::

   pipx install git+https://github.com/pitt-crc/quota_notifier.git

If you are working as a developer, installation options are provided for extra dependencies:

.. code-block:: bash

   pipx install quota_notifier.[all]

To install a specific subset of extras, chose from the following options:

+----------------------+---------------------------------------------------------+
| Install Option       | Description                                             |
+======================+=========================================================+
| ``[all]``            | Install all extra dependencies listed in this table.    |
+----------------------+---------------------------------------------------------+
| ``[docs]``           | Dependencies required for building HTML documentation.  |
+----------------------+---------------------------------------------------------+
| ``[tests]``          | Dependencies required for running tests with coverage.  |
+----------------------+---------------------------------------------------------+

Configuration
-------------

.. todo
