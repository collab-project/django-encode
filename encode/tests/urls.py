# Copyright Collab 2014-2015

"""
URLConf for :py:mod:`encode` tests.
"""

from django.contrib import admin
from django.conf.urls import include, url


admin.autodiscover()

urlpatterns = [
    url(r'^', include(admin.site.urls)),
]
