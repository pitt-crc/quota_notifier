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

    with path.open() as req_file:
        return req_file.read().splitlines()


def get_package_data(directory):
    """Return a list of files in the given directory"""

    return list(map(str, directory.rglob('*')))


def get_extras(**paths):
    """Return a dictionary of package extras

    Values for `tests` and `all` are generated automatically
    """

    extras = {'all': set(), 'tests': ['coverage'], }
    for extra_name, path in paths.items():
        extras[extra_name] = get_requirements(path)

    for packages in extras.values():
        extras['all'].update(packages)

    return extras


def get_meta(value):
    """Return package metadata as defined in the init file

    Args:
        value: The metadata variable to return a value for
    """

    init_path = _file_dir / 'app' / '__init__.py'
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
        notifier=app.cli:Application.execute
    """,
    install_requires=get_requirements(_pkg_requirements_path),
    extras_require=get_extras(docs=_doc_requirements_path),
    author=get_meta('author'),
    keywords='disk usage quota notify email',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    license=get_meta('license'),
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)
