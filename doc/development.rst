Development
===========

After checkout, install dependencies and package in active virtualenv::

  $ pip -e git+https://github.com/thijstriemstra/python-video-converter.git#egg=python-video-converter
  $ pip install -e .
  $ pip install -r encode/tests/requirements.txt


Testing
-------

Running tests with Tox_::

  $ tox -v

Or alternatively::

  $ python setup.py test

Running tests without Tox_::

  $ ./runtests.py

Directly with ``django-admin``::

  $ django-admin test --settings=encode.tests.settings encode


Coverage
--------

To generate a test coverage report using `coverage.py`_::

  $ coverage run --source='.' runtests.py
  $ coverage html

The resulting HTML report can be found in the ``htmlcov`` directory.


Localization
------------

To collect all strings for the locale ``nl`` into ``django.po``::

  $ django-admin makemessages --settings=encode.tests.settings --ignore=tests/*.py -l nl

After translating, compile the ``django.po`` catalog into the binary
version `django.mo`::

  $ django-admin compilemessages --settings=encode.tests.settings


Documentation
-------------

Install Sphinx::

  $ pip install sphinx>=1.1.0

Change to the ``doc`` directory and run::

  $ make html

The resulting HTML output can be found in the ``doc/_build/html`` directory.


.. _Tox: http://tox.testrun.org/
.. _coverage.py: http://nedbatchelder.com/code/coverage/
