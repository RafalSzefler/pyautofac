import os
import re
import sys
from setuptools import setup, find_packages
try:
    from pip.req import parse_requirements
except ImportError:
    from pip._internal.req import parse_requirements


ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = 'pyautofac'
PROJECT_PATH = os.path.join(ROOT, PROJECT_NAME)
VERSION_RE = re.compile(r'^__version__\s*=\s*\'(?P<version>\d*(\.\d*){0,2})\'\s*$')
AUTHOR = ('Rafal Szefler-Tyrowicz', 'rafal.szefler.tyrowicz@gmail.com')


def read_file(path):
    with open(os.path.join(ROOT, path), 'r') as fo:
        return fo.read()


def read_requirements(path):
    requirements = parse_requirements(path, session=False)
    return [str(ir.req) for ir in requirements]


def get_version():
    ini = os.path.join(PROJECT_PATH, '__init__.py')
    with open(ini, 'r') as fo:
        for line in fo:
            match = VERSION_RE.match(line)
            if match:
                return match.groupdict()['version']
    raise Exception('__version__ not found in %s/__init__.py' % PROJECT_NAME)


if sys.version_info < (3, 5):
    print('pyautofac works only with Python3.5+')
    sys.exit(1)

version = get_version()
print(PROJECT_NAME, version)
print()

setup(
    name=PROJECT_NAME,
    version=version,
    description=PROJECT_NAME,
    long_description=read_file('README.md'),
    author=AUTHOR[0],
    author_email=AUTHOR[1],
    tests_require=read_requirements('requirements.test.txt'),
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_dir={PROJECT_NAME: PROJECT_NAME},
)

