#!/usr/bin/env python
# Copyright Collab 2012-2017
# See LICENSE for details.

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# get version nr
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
    'encode')))
from encode import version  # flake8: noqa
sys.path.pop(0)


class Tox(TestCommand):
    """
    Makes the `python setup.py test` command work with Tox.
    """
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name='django-encode',
    packages=find_packages(),
    include_package_data=True,
    cmdclass={'test': Tox},
    version=version,
    description='Django media encoding.',
    long_description=README,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    author='Collab',
    author_email='info@collab.nl',
    url='http://github.com/collab-project/django-encode',
    license='MIT',
    install_requires=[
        'celery>=3.1,<4.0',
        'django-appconf>=0.6',
        'django-queued-storage>=0.8.0'
    ],
    tests_require=[
        'tox'
    ],
)
