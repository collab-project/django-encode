# Copyright Collab 2013-2015

"""
Celery configuration for the :py:mod:`encode` application.
"""

from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encode.tests.settings')

# create instance of the library
app = Celery('encode')

# add the Django settings module as a configuration source for Celery
app.config_from_object('django.conf:settings')

# Automatically discover tasks in reusable apps.
# Wraps access to the settings object in a lambda to ensure that the settings
# object is not prepared prematurely.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
