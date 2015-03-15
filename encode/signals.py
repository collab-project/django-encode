# Copyright Collab 2012-2015

"""
Signals.
"""

from __future__ import unicode_literals

import logging

from django.core.files.base import File


logger = logging.getLogger(__name__)


def check_file_changed(sender, **kwargs):
    """
    Compare 2 files byte by byte when uploading a file.
    """
    instance = kwargs['instance']
    if instance.id and instance.input_file:
        if isinstance(instance.input_file.file, File):
            instance.encoding = True
