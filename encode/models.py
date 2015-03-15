# Copyright Collab 2012-2015

"""
Models.
"""

from __future__ import unicode_literals

import os
import shlex
import logging
import socket

from django.db import models
from django.db.models.signals import pre_save
from django.core.files.base import File as DjangoFile
from django.core.files.storage import get_storage_class
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.models import User

from queued_storage.fields import QueuedFileField
from queued_storage.backends import QueuedStorage

from encode.conf import settings
from encode.signals import check_file_changed
from encode import UploadError, FILE_TYPES, VIDEO, AUDIO, SNAPSHOT
from encode.util import get_random_filename, get_media_upload_to, short_path


__all__ = ['MediaFile', 'Encoder', 'EncodingProfile', 'MediaBase', 'Audio',
           'Video', 'Snapshot']

logger = logging.getLogger(__name__)

# storages
cdnStorage = get_storage_class(settings.ENCODE_CDN_FILE_STORAGE)()
queuedStorage = QueuedStorage(
    local=settings.ENCODE_LOCAL_FILE_STORAGE,
    remote=settings.ENCODE_REMOTE_FILE_STORAGE,
    local_options=settings.ENCODE_LOCAL_STORAGE_OPTIONS,
    remote_options=settings.ENCODE_REMOTE_STORAGE_OPTIONS,
    delayed=True)


@python_2_unicode_compatible
class MediaFile(models.Model):
    """
    Model for media files.
    """
    title = models.CharField(
        _('Title'),
        help_text=_('Title for this file.'),
        max_length=255,
        blank=True,
        null=True,
    )
    file = models.FileField(
        help_text=_('File for this model.'),
        # files are stored remotely
        storage=cdnStorage,
        upload_to=get_media_upload_to,
    )

    created_at = models.DateTimeField(
        _('Created at'),
        help_text=_('The date and time the file was created.'),
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        _('Modified at'),
        help_text=_('The date and time the file was last modified.'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Media file')
        verbose_name_plural = _('Media files')

    def __str__(self):
        return self.title or os.path.basename(self.file.name)


@python_2_unicode_compatible
class Encoder(models.Model):
    """
    Encoder model for tool like FFmpeg or ImageMagick.
    """
    name = models.CharField(
        _("Name"),
        null=False,
        blank=False,
        max_length=255,
        help_text=_(
            "Name for this encoder. Example: FFmpeg"
        )
    )
    description = models.TextField(
        _("Description"),
        null=True,
        blank=True,
        help_text=_('Optional description for this encoder.')
    )
    documentation_url = models.URLField(
        _("Documentation URL"),
        null=True,
        blank=True,
        max_length=255,
        help_text=_(
            "URL for the external documentation of this encoder."
        )
    )
    path = models.CharField(
        _("Path"),
        null=False,
        blank=False,
        max_length=255,
        help_text=_(
            "Name or path of the encoder executable. Example: "
            "/usr/local/bin/ffmpeg"
        )
    )
    klass = models.CharField(
        _('Class'),
        null=True,
        blank=True,
        max_length=255,
        help_text=_(
            "Optional encoder class to use. Example: "
            "encode.encoders.FFMpegEncoder"
        )
    )
    command = models.CharField(
        _('Command'),
        null=True,
        blank=True,
        max_length=255,
        help_text=_(
            "Optional command options that are always added. Example: "
            "-loglevel fatal -y"
        )
    )

    created_at = models.DateTimeField(
        _('Created at'),
        help_text=_('The date and time the encoder was created.'),
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        _('Modified at'),
        help_text=_('The date and time the encoder was last modified.'),
        auto_now=True
    )

    @property
    def encode_cmd(self):
        """
        The full command for the encoder, eg. ``ffmpeg -loglevel fatal -y``.

        :return: A list of options that represent the encoder base command.
        :rtype: list
        """
        cmd = shlex.split(self.path)
        if self.command:
            # append options, if any
            return cmd + shlex.split(self.command)
        return cmd

    class Meta:
        verbose_name = _('Encoder')
        verbose_name_plural = _('Encoders')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class EncodingProfile(models.Model):
    """
    Job data for encoding a file.
    """
    name = models.CharField(
        _('Name'),
        max_length=255,
        help_text=_(
            "Title for this encoding profile. Example: WebM"
        )
    )
    description = models.TextField(
        _('Description'),
        null=True,
        blank=True,
        help_text=_('Optional description for this encoding profile.')
    )
    mime_type = models.CharField(
        _('MIME-type'),
        null=True,
        blank=True,
        max_length=255,
        help_text=_(
            "MIME-type for this encoding profile. Example: video/webm"
        )
    )
    container = models.CharField(
        _('Container'),
        max_length=50,
        help_text=_("Media container (file extension). Example: webm")
    )
    video_codec = models.CharField(
        _('Video Codec'),
        null=True,
        blank=True,
        max_length=255,
        help_text=_("Video codec name. Example: VP8")
    )
    audio_codec = models.CharField(
        _('Audio Codec'),
        null=True,
        blank=True,
        max_length=255,
        help_text=_("Audio codec name. Example: Vorbis")
    )
    encoder = models.ForeignKey(
        Encoder,
        null=True,
        help_text=_("Encoder for this profile.")
    )
    command = models.TextField(
        _('Command'),
        null=False,
        help_text=_(
            "The command to execute, excluding the encoder executable's path "
            'or name. Supports variable interpolation. Example: -i "{input}" '
            '-acodec libvorbis -ab 128k -vcodec libvpx -s 320x240 "{output}"'
        )
    )

    created_at = models.DateTimeField(
        _('Created at'),
        help_text=_('The date and time the profile was created.'),
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        _('Modified at'),
        help_text=_('The date and time the profile was last modified.'),
        auto_now=True
    )

    @property
    def encode_cmd(self):
        """
        The command for the encoder without the vars injected, eg.
        ``ffmpeg -y -i "{input}" "{output}"``.

        :return: A string that represents the command that the encoder
                 should execute.
        :rtype: str
        """
        return " ".join(self.encoder.encode_cmd + shlex.split(self.command))

    class Meta:
        ordering = ["-name"]
        verbose_name = _('Encoding profile')
        verbose_name_plural = _('Encoding profiles')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class MediaBase(models.Model):
    """
    Base model for media objects.
    """
    title = models.CharField(
        _('Title'),
        max_length=255,
        help_text=_('Title for this object.')
    )
    file_type = models.CharField(
        _('File type'),
        max_length=255,
        choices=FILE_TYPES
    )
    input_file = QueuedFileField(
        _('Input file'),
        # source file is stored and encoded locally into one or more files,
        # which are then moved to the cloud by storing them in
        # self.output_files. If self.keep_input_file is True (default is
        # False), then self.input_file will *not* be deleted from the
        # webserver serving the Django application.
        upload_to=get_media_upload_to,
        storage=queuedStorage,
        help_text=_("The uploaded source file."),
        null=True,
        blank=True,
    )
    uploaded = models.BooleanField(
        _('Uploaded'),
        default=False,
        editable=False,
        help_text=_(
            "Indicates that the output file(s) have been uploaded.")
    )
    encoded = models.BooleanField(
        _('Encoded'),
        default=False,
        editable=False,
        help_text=_("Indicates that the input file has finished encoding.")
    )
    encoding = models.BooleanField(
        _('Encoding'),
        default=False,
        editable=False,
        help_text=_("Indicates that the input file is currently encoding.")
    )
    keep_input_file = models.BooleanField(
        _('Keep input file'),
        default=False,
        help_text=_(
            """Indicates that the input file should be saved and not
            be removed after it's encoded and uploaded.""")
    )

    # related fields
    profiles = models.ManyToManyField(
        EncodingProfile,
        null=True,
        help_text=_('The encoding profile(s).'),
        related_name='encoding_profiles',
        verbose_name=_('Encoding profiles'),
    )
    output_files = models.ManyToManyField(
        MediaFile,
        null=True,
        blank=True,
        help_text=_('The encoded output file(s). Stored in CDN.'),
        related_name='encoding_profiles',
        verbose_name=_('Output files'),
    )
    user = models.ForeignKey(
        User,
        null=True,
        help_text=_("The user who uploaded the input file.")
    )

    created_at = models.DateTimeField(
        _('Created at'),
        help_text=_('The date and time the object was created.'),
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        _('Modified at'),
        help_text=_('The date and time the object was last modified.'),
        auto_now=True
    )

    @property
    def ready(self):
        """
        Indicates if all output files have completed encoding.

        :return: Boolean indicating if all output files have completed
            encoding.
        :rtype: boolean
        """
        if self.id:
            return self.output_files.count() == self.profiles.count()

        return False

    @property
    def encodable(self):
        """
        Indicates if the input file has not completed encoding yet.

        :return: Boolean indicating if the input file has not completed
            encoding yet.
        :rtype: boolean
        """
        return not self.encoded

    @property
    def input_path(self):
        """
        The path to the input file uploaded by the user.

        :return: For example: ``[MEDIA_ROOT]/user/video/IMG001.MPEG``.
        :rtype: str or ``None``
        """
        if self.input_file:
            return os.path.join(settings.ENCODE_MEDIA_ROOT,
                self.input_file.name)

        return None

    def output_path(self, profile):
        """
        The path of the encoded output file.

        :param profile: The :py:class:`EncodingProfile` instance that contains
            the encoding data.
        :type profile: :py:class:`EncodingProfile`
        :return: For example:
            ``[ENCODE_MEDIA_ROOT]/[ENCODE_MEDIA_PATH_NAME]/audio/51.mp3``.
        :rtype: str
        """
        return os.path.join(
            settings.ENCODE_MEDIA_ROOT,
            settings.ENCODE_MEDIA_PATH_NAME,
            self.file_type,
            "{id}.{container}".format(
            container=profile.container,
            id=self.id
        ))

    def get_media(self):
        """
        The media type. Either ``VIDEO``, ``SNAPSHOT``, or ``AUDIO``.

        :rtype: :py:class:`MediaBase` subclass.
        :return: The media subclass.
        """
        if self.file_type == VIDEO:
            return self.video
        elif self.file_type == AUDIO:
            return self.audio
        elif self.file_type == SNAPSHOT:
            return self.snapshot

    def store_file(self, profile):
        """
        Add the encoded input file to the ``output_files`` field.

        :param profile: The :py:class:`EncodingProfile` instance that contains
            the encoding data.
        :type profile: :py:class:`EncodingProfile`
        :raises: :py:class:`~encode.UploadError`: Something went wrong while
            uploading the file or the file does not exist.
        """
        # use random name for (encoded) output file
        file_name = get_random_filename(profile.container)
        path = self.output_path(profile)

        logger.info("Saving encoded file {0} in storage as {1}".format(
            short_path(path), file_name))

        if os.path.exists(path):
            # put encoded file in external storage
            with open(path, 'rb') as encoded_file:

                media_file = MediaFile(title=file_name)
                try:
                    media_file.file.save(file_name, DjangoFile(encoded_file))
                    self.output_files.add(media_file)

                    logger.info("Stored {0} at {1}".format(file_name,
                        media_file.file.url))

                except socket.error as error:  # pragma: no cover
                    raise UploadError(error)
        else:
            raise UploadError("{} does not exist".format(path))

        # when all output_files have been saved (cq. uploaded)
        if self.ready:
            self.encoded = True
            self.encoding = False
            self.uploaded = True
        self.save()

    def remove_file(self, profile):
        """
        Remove the input (and possible local encoded) file.

        :param profile: The :py:class:`EncodingProfile` instance that contains
            the encoding data.
        :type profile: :py:class:`EncodingProfile`
        """
        # when all output_files have been saved (cq. uploaded)
        if self.ready and not self.keep_input_file:
            input_path = str(self.input_path)

            logger.debug(
                "Removing original input file in remote storage: {0}".format(
                self.input_file.file))

            # remove original file in remote storage of input_file field
            self.input_file.delete(save=False)

            # remove original file in local storage of input file
            if os.path.exists(input_path):
                logger.debug(
                    "Removing original input file in local storage: "
                    "{0}".format(short_path(input_path))
                )
                os.remove(input_path)

        # remove encoded file
        path = self.output_path(profile)
        if os.path.exists(path):
            logger.debug("Removing local encoded file: {0}".format(
                short_path(path)))
            os.remove(path)

        self.save()

    def save(self, profiles=[], *args, **kwargs):
        """
        Set the ``encoding`` status to ``True`` and save the model.

        :param profiles: List of primary keys of encoding profiles.
        :type profiles: `list`
        """
        # the model has not been saved before
        if not self.id:
            # the output files have not completed encoding yet
            if not self.ready:
                # enable the encoding flag
                self.encoding = True

        super(MediaBase, self).save(*args, **kwargs)

        # the input file has not completed encoding yet but it exists on
        # the local disk and is ready to be processed
        if self.encodable and self.input_path:
            # import the tasks here to prevent a circular import
            from encode.tasks import EncodeMedia, StoreMedia

            # transfer input file from local disk to remote encoder *once*
            if self.output_files.count() == 0:
                try:
                    # transfer_file is a celery.result.EagerResult instance
                    transfer_file = self.input_file.transfer()

                    logger.debug("Transferred file: {} (success: {})".format(
                        short_path(self.input_path),
                        transfer_file.result))

                except Exception as e:  # pragma: no cover
                    logger.error("Error transferring file: {}".format(e))
                    raise

            # encode input files on encoder
            # XXX: chain these tasks
            for profile_id in profiles:
                try:
                    # get the encoding profile
                    profile = EncodingProfile.objects.get(id=profile_id)

                except EncodingProfile.DoesNotExist:
                    logger.error("Cannot encode: EncodingProfile with pk '{0}'"
                        " does not exist.".format(profile_id))
                    raise

                encode_media = EncodeMedia()
                store_media = StoreMedia()
                encode_media.apply_async(
                    args=[profile, self.id, self.input_path,
                          self.output_path(profile)],
                    # XXX: don't hardcode
                    queue='encoder',
                    routing_key='media.encode',
                    # add callback to transfer output file(s) from encoder to
                    # cdn
                    link=store_media.s()
                )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Media File")
        verbose_name_plural = _("Media Files")

    def __str__(self):
        return self.title


class Video(MediaBase):
    """
    Model for video files.
    """
    def save(self, *args, **kwargs):
        """
        Encode and upload the video.
        """
        if not self.id:
            self.file_type = VIDEO

        super(Video, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Video Clip")
        verbose_name_plural = _("Video Clips")

pre_save.connect(check_file_changed, sender=Video)


class Audio(MediaBase):
    """
    Model for audio files.
    """
    def save(self, *args, **kwargs):
        """
        Encode and upload the audio clip.
        """
        if not self.id:
            self.file_type = AUDIO

        super(Audio, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Audio Clip")
        verbose_name_plural = _("Audio Clips")

pre_save.connect(check_file_changed, sender=Audio)


class Snapshot(MediaBase):
    """
    Model for snapshot files.
    """
    def save(self, *args, **kwargs):
        """
        Encode and upload the snapshot file.
        """
        if not self.id:
            self.file_type = SNAPSHOT

        super(Snapshot, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Snapshot")
        verbose_name_plural = _("Snapshots")

pre_save.connect(check_file_changed, sender=Snapshot)
