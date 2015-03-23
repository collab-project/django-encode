# Copyright Collab 2012-2015

"""
Utilities.
"""

from __future__ import unicode_literals

import os
import logging
import binascii
from base64 import b64decode
from tempfile import NamedTemporaryFile

from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
from django.utils.crypto import get_random_string

from encode.conf import settings
from encode import DecodeError, EncodeError


__all__ = ["fqn", "get_random_filename", "get_media_upload_to", "parseMedia",
           "storeMedia", "TemporaryMediaFile"]

logger = logging.getLogger(__name__)


def fqn(obj):
    """
    Get fully qualified name of ``obj``, eg. ``encode.util.fqn``.

    :param obj:
    :type obj:
    :rtype: str
    """
    return ".".join([obj.__module__, obj.__class__.__name__])


def get_random_filename(file_extension='png', length=12):
    """
    Returns a random filename with an optional length and file-extension.

    :param file_extension: File extension for the file, e.g. 'gif'.
    :type file_extension: str
    :param length: Number of random characters the filename should contain.
    :type length: int
    :rtype: str
    :returns: A random filename, e.g. ``4AwV8Ckn65a3.png``.
    """
    return get_valid_filename(
        '{random_string}.{extension}'.format(
        random_string=get_random_string(length),
        extension=file_extension
    ))


def get_media_upload_to(instance, filename):
    """
    Get target path for user file uploads.

    :param instance: Model instance.
    :type instance: :py:class:`django.db.models.Model`
    :param filename: The filename for the file being uploaded, eg. 'test.png'.
    :type filename: str
    :rtype: str
    """
    if hasattr(instance, 'file_type'):
        file_type = instance.file_type
    else:
        file_type = 'files'

    url = '{category}/{file_type}/{filename}'.format(
        category=settings.ENCODE_MEDIA_PATH_NAME,
        file_type=file_type,
        filename=filename)
    return url


def short_path(path, base='ENCODE_MEDIA_ROOT'):
    """

    :param path:
    :type path: str
    :param base:
    :type base: str
    :rtype: str
    :returns:
    """
    return "{}{}".format(base, path[len(getattr(settings, base)):])


def parseMedia(data):
    """
    Decode base64-encoded media data and return result.

    :param data: base64-encoded string
    :type data: str
    :rtype: str
    """
    #logger.debug("Got frame data: %s" % str(len(data)))
    #logger.debug("Data URI header: %s" % data[0:40])

    try:
        header_len = data.find(",")
        payload = data[header_len + 1:]
        binary = b64decode(payload)
        #logger.debug("Binary id: %s" % binary[0:4])

        return binary

    except (AttributeError, TypeError, binascii.Error):
        # corrupt media
        raise DecodeError("Corrupt media")


def storeMedia(model, inputFileField, title, profiles, fpath):
    """
    Encode and store :py:class:`~encode.models.MediaBase` object.

    :param model: A model object or instance, e.g.
        :py:class:`~encode.models.Video`.
    :type model: class
    :ivar inputFileField: Name of the model field where the file will be
        stored.
    :type inputFileField: str
    :param title: Name of the file, e.g. `test.png`.
    :type title: str
    :param profiles: List of :py:class:`~encode.models.EncodingProfile` names.
    :type profiles: list
    :param fpath: Location of media file.
    :type fpath: str
    :rtype: :py:class:`~encode.models.MediaBase` subclass.
    """
    # create new media object
    mediaObj = model()
    mediaObj.title = title
    mediaObj.save()

    logger.debug("Created {} object: {}".format(fqn(mediaObj), mediaObj))

    # prevent circular import
    from encode.models import EncodingProfile

    # add encoding profiles
    if len(profiles) > 0:
        logger.debug("Profiles for {}: {}".format(mediaObj,
            ", ".join(profiles)))

        for profile_name in profiles:
            try:
                profile = EncodingProfile.objects.get(name=profile_name)
                mediaObj.profiles.add(profile)
            except EncodingProfile.DoesNotExist:
                raise EncodeError("Profile '{}' does not exist".format(
                    profile_name))

    # attach file to model
    with open(fpath, 'rb') as file_data:
        logger.debug("Storing data from {} in model field: {}".format(
            fpath, inputFileField))

        # get raw file data
        data = ContentFile(file_data.read(), title)

        # store file data but don't save related model until
        # the encoding profiles are saved as well
        getattr(mediaObj, inputFileField).save(title, data, save=False)

    # save by passing in primary keys of encoding profiles
    mediaObj.save(profiles=[x.pk for x in mediaObj.profiles.all()])

    logger.debug("File for model field {} stored at: {}".format(
        inputFileField, getattr(mediaObj, inputFileField).file))

    return mediaObj


class TemporaryMediaFile(object):
    """
    Container to store a temporary media file for encoding.

    :param prefix: The prefix to use for the temporary filename, e.g.
        ``video_``.
    :type prefix: str
    :param model: The model to store the file on, e.g. a subclass of
        :py:class:`~encode.models.MediaBase`.
    :type model: :py:class:`django.db.models.Model`
    :param inputFileField: Name of the model field where the file will be
        stored.
    :type inputFileField: str
    :param profiles: List of :py:class:`~encode.models.EncodingProfile`
        names, e.g. ``[u"MP4", u"WebM Audio/Video"]``
    :type profiles: list
    :param extension: The extension to use for the temporary filename.
        Defaults to ``media``.
    :type extension: str
    """
    def __init__(self, prefix, model, inputFileField, profiles,
        extension='media'):
        self.prefix = prefix
        self.model = model
        self.profiles = profiles
        self.inputFileField = inputFileField
        self.extension = extension

    def save(self, fileData):
        """
        Save ``fileData`` in temporary file and start encoding.

        :param fileData: The media bytes.
        :type fileData: :py:class:`io.BytesIO`
        :rtype: :py:class:`~encode.models.MediaBase`
        :returns: A new instance of type ``self.model``.
        """
        # save data to temporary file.
        # XXX: Seems unncessary because its already stored in input_file
        #      and then transferred to the remote server?
        with NamedTemporaryFile(
            prefix=self.prefix,
            suffix="." + self.extension,
            delete=False
            ) as media_file:
            media_file.write(fileData.getvalue())

        if os.path.exists(media_file.name):
            logger.debug("Stored media data in temporary file: {}".format(
                media_file.name))

            # encode and store media file
            mediaObj = storeMedia(
                model=self.model,
                inputFileField=self.inputFileField,
                title=get_random_filename(file_extension=self.extension),
                profiles=self.profiles,
                fpath=media_file.name
            )

            logger.debug("Removing temporary media file: {}".format(
                media_file.name))

            # remove temporary file
            os.remove(media_file.name)

            return mediaObj
