# Copyright Collab 2014-2015

"""
Custom test runner.
"""

from __future__ import unicode_literals

import shutil
import logging

from django.conf import settings
from django.test.runner import DiscoverRunner

logger = logging.getLogger(__name__)


class TempMediaMixin(object):
    """
    Mixin that removes `MEDIA_ROOT` directory when test runner completes.
    """
    def teardown_test_environment(self):
        """
        Delete storage.
        """
        super(TempMediaMixin, self).teardown_test_environment()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


class CustomTestSuiteRunner(TempMediaMixin, DiscoverRunner):
    """
    Test suite runner that stores local files in a temporary directory.
    """
