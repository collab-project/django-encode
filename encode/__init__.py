# Copyright Collab 2012-2015

"""
`django-encode` application.
"""

from __future__ import unicode_literals

AUDIO = "audio"
VIDEO = "video"
SNAPSHOT = "snapshot"

#: Accepted file types.
FILE_TYPES = (
    (AUDIO, "Audio"),
    (VIDEO, "Video"),
    (SNAPSHOT, "Snapshot"),
)

#: Application version.
__version__ = (1, 0, 2)


def short_version(version=None):
    """
    Return short application version. For example: `1.0.0`.
    """
    v = version or __version__
    return '.'.join([str(x) for x in v[:3]])


def get_version(version=None):
    """
    Return full version nr, inc. rc, beta etc tags.

    For example: `2.0.0a1`
    :rtype: str
    """
    v = version or __version__
    if len(v) == 4:
        return '{0}{1}'.format(short_version(v), v[3])

    return short_version(v)


#: Full version number.
version = get_version()


class EncodeError(Exception):
    """
    Something bad happened while encoding the media.
    """
    pass


class DecodeError(Exception):
    """
    Something bad happened while decoding the media.
    """
    pass


class UploadError(Exception):
    """
    Something bad happened while uploading the encoded media.
    """
    pass
