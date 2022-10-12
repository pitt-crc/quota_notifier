"""Package installation logic"""

import re
from pathlib import Path

from setuptools import find_packages, setup

_file_dir = Path(__file__).resolve().parent
_pkg_requirements_path = _file_dir / 'requirements.txt'
_doc_requirements_path = _file_dir / 'docs' / 'requirements.txt'


def get_long_description():
    """Return a long description of the parent package"""

    readme_file = _file_dir / 'README.md'
    return readme_file.read_text()


def get_requirements(path):
    """Return a list of package dependencies"""

    return path.read_text().splitlines()


def get_package_data(directory):
    """Return a list of files in the given directory"""

    return list(map(str, directory.rglob('*')))


def get_extras(**extras_items):
    """Return a dictionary of package extras

    Argument names are used to generate key values in the returned dictionary.
    Argument values can be a list of packages or the path to a requirements
    file. The `all` key is added to the returned dictionary automatically.

    Args:
        **extra sets of dependencies as a list of packages or requirements path
    """

    extras = dict()
    for extra_name, extra_definition in extras_items.items():
        if isinstance(extra_definition, Path):
            extras[extra_name] = get_requirements(extra_definition)

        else:
            extras[extra_name] = extra_definition

    extras['all'] = set()
    for packages in extras.values():
        extras['all'].update(packages)

    return extras


def get_meta(value):
    """Return package metadata as defined in the init file

    Args:
        value: The metadata variable to return a value for
    """

    init_path = _file_dir / 'quota_notifier' / '__init__.py'
    init_text = init_path.read_text()

    regex = re.compile(f"__{value}__ = '(.*?)'")
    value = regex.findall(init_text)[0]
    return value


setup(
    name='quota_notifier',
    description='Automatic email notification tool for disk quota usage.',
    version=get_meta('version'),
    packages=find_packages(),
    python_requires='>=3.9',
    entry_points="""
        [console_scripts]
        notifier=quota_notifier.cli:Application.execute
    """,
    install_requires=get_requirements(_pkg_requirements_path),
    extras_require=get_extras(docs=_doc_requirements_path, tests=['coverage']),
    author=get_meta('author'),
    keywords='disk usage quota notify email',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    license=get_meta('license'),
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)
