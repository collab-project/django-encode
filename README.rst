django-encode
=============

``django-encode`` allows you to encode and transfer media files async.

.. image:: https://img.shields.io/pypi/v/django-encode.svg
    :target: https://pypi.python.org/pypi/django-encode
.. image:: https://img.shields.io/pypi/pyversions/django-encode.svg
    :target: https://pypi.python.org/pypi/django-encode
.. image:: https://travis-ci.org/collab-project/django-encode.svg?branch=master
    :target: https://travis-ci.org/collab-project/django-encode
.. image:: https://coveralls.io/repos/collab-project/django-encode/badge.svg
    :target: https://coveralls.io/r/collab-project/django-encode
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/collab-project/django-encode/master/LICENSE


Installation
------------

Use pip_ to install the download and install the package from PyPi_::

  pip install django-encode

Or checkout the source code from Github_::

  git clone https://github.com/collab-project/django-encode.git
  cd django-encode
  pip install -e .

The dependency ``python-video-converter`` is not available on PyPi and needs to be installed
manually. This installs a fork of ``python-video-converter`` that supports ffmpeg 2.x and newer::

  pip install -e git+https://github.com/thijstriemstra/python-video-converter.git#egg=python-video-converter


Documentation
-------------

Documentation can be found on `readthedocs.io`_.


.. _pip: https://pypi.python.org/pypi/pip
.. _PyPi: https://pypi.python.org/pypi/django-encode
.. _readthedocs.io: https://django-encode.readthedocs.io/en/latest
.. _Github: https://github.com/collab-project/django-encode