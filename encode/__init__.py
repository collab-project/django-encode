# Copyright Collab 2012-2015

"""
`django-encode` application.
"""

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
__version__ = (1, 0, 0, 'rc1')

#: Short application version. For example: `1.0.0`
short_version = '.'.join([str(x) for x in __version__[:3]])

#: For example: `2.0.0a1`
if len(__version__) == 4:
    version = '{0}{1}'.format(short_version, __version__[3])
else:
    version = short_version


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
