# Copyright Collab 2013-2015

"""
Configuration options.
"""

from __future__ import unicode_literals

import os

from django.conf import settings

from appconf import AppConf


class EncodeConf(AppConf):
    """
    Configuration settings.
    """
    #: Name of the root directory holding the user-uploaded files.
    MEDIA_PATH_NAME = "encode"

    #: Absolute filesystem path to the directory that will hold user-uploaded
    #: files for the encode application.
    MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, MEDIA_PATH_NAME)

    #: TODO
    AUDIO_PROFILES = []

    #: TODO
    VIDEO_PROFILES = []

    #: TODO
    IMAGE_PROFILES = []

    #: TODO
    LOCAL_FILE_STORAGE = settings.LOCAL_FILE_STORAGE

    #: Django file storage used for transferring media uploads to the encoder.
    REMOTE_FILE_STORAGE = LOCAL_FILE_STORAGE

    #: Django file storage used for storing encoded media on a CDN network.
    CDN_FILE_STORAGE = LOCAL_FILE_STORAGE

    #: TODO
    LOCAL_STORAGE_OPTIONS = dict(
        # Absolute path to the local directory that will hold user-uploaded
        # files.
        location=MEDIA_ROOT
    )

    #: TODO
    REMOTE_STORAGE_OPTIONS = dict(
        # Absolute path to the remote directory that will hold transferred
        # media files.
        location=os.path.join(MEDIA_ROOT, "remote")
    )

    #: TODO
    DEFAULT_ENCODER_CLASS = "encode.encoders.BasicEncoder"

    # override the default prefix
    CACHE_PREFIX = 'encode'
