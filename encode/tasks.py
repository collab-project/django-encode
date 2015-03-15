# Copyright Collab 2012-2015

"""
Tasks.
"""

from __future__ import unicode_literals

from celery import Task
from celery.utils.log import get_task_logger

from encode.models import MediaBase
from encode.util import fqn, short_path
from encode import EncodeError, UploadError
from encode.encoders import get_encoder_class


__all__ = ['EncodeMedia', 'StoreMedia']

logger = get_task_logger(__name__)


def media_base(obj_id):
    """
    :param obj_id: The primary key of the :py:class:`~encode.models.MediaBase`
        model.
    :type obj_id: int
    :rtype: :py:class:`~encode.models.MediaBase` instance
    :returns: The :py:class:`~encode.models.MediaBase` instance in question.
    """
    try:
        # get the object by id
        base = MediaBase.objects.get(pk=obj_id)
    except MediaBase.DoesNotExist:
        logger.error(
            "Cannot encode: Media with pk '{0}' does not exist.".format(
            obj_id), exc_info=True
        )
        raise

    return base


class EncodeMedia(Task):
    """
    Encode a :py:class:`~encode.models.MediaBase` model's ``input_file``.
    """
    def run(self, profile, media_id, input_path, output_path):
        """
        Execute the task.

        :param profile: The :py:class:`~encode.models.EncodingProfile`
            instance.
        :type profile: :py:class:`~encode.models.EncodingProfile`
        :param media_id: The primary key of the
            :py:class:`~encode.models.MediaBase` model.
        :type media_id: int
        :param input_path:
        :type input_path: str
        :param output_path:
        :type output_path:

        :rtype: dict
        :returns: Dictionary with ``id`` (media object's id) and ``profile``
            (encoding profile instance).
        """
        # find encoder
        Encoder = get_encoder_class(profile.encoder.klass)
        encoder = Encoder(profile, input_path, output_path)

        logger.debug("***** New '{}' encoder job *****".format(profile))
        logger.debug("Loading encoder: {0} ({1})".format(profile.encoder,
            fqn(encoder)))
        logger.debug("Encoder command: {0}".format(encoder.command))
        logger.info("Encoder input file: {0}".format(
            short_path(encoder.input_path)))

        logger.info("Start encoding ({0}) - output file: {1}".format(
            profile.mime_type,
            short_path(encoder.output_path)),

            # additional information for sentry
            extra={
               'encoder_profile': profile,
               'encoder_name': profile.encoder,
               'encoder_command': encoder.command,
               'encoder_output': encoder.output_path
           })

        # start encoding
        try:
            encoder.start()
        except EncodeError as error:
            error_msg = "Encoding Media failed: {0}".format(
                encoder.input_path)

            logger.error(error_msg, exc_info=True, extra={
                'output': error.output,
                'command': error.command
            })
            raise

        logger.debug("Completed encoding ({0}) - output file: {1}".format(
            profile.mime_type, short_path(encoder.output_path)))

        return {
            "id": media_id,
            "profile": profile
        }


class StoreMedia(Task):
    """
    Upload an instance :py:class:`~encode.models.MediaBase` model's
    ``output_files`` m2m field.
    """
    #: If enabled the worker will not store task state and return values
    #: for this task.
    ignore_result = True

    def run(self, data):
        """
        Execute the task.

        :param data:
        :type data: dict
        """
        media_id = data.get('id')
        profile = data.get('profile')
        base = media_base(media_id)
        media = base.get_media()

        logger.debug("Uploading encoded file: {0}".format(
            short_path(media.output_path(profile))))

        try:
            # store the media object
            media.store_file(profile)
        except (UploadError, Exception) as exc:
            # XXX: handle exception: SSLError('The read operation timed out',)
            logger.error("Upload media failed: '{0}' - retrying ({1})".format(
                media, exc), exc_info=True)
            raise

        logger.info("Upload complete: {0}".format(
            short_path(media.output_path(profile))), extra={
            'output_files': [x.file.url for x in media.output_files.all()],
        })

        # remove the original input file
        if media.keep_input_file is False:
            media.remove_file(profile)
