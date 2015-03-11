Development
===========

Testing
-------

Running tests with Tox_::

  $ tox -v

Or alternatively::

  $ python setup.py test

Running tests without Tox_::

  $ ./runtests.py

Directly with `django-admin`::

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


.. _Tox: http://tox.testrun.org/
.. _coverage.py: http://nedbatchelder.com/code/coverage/
