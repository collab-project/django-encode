# Copyright Collab 2013-2015

"""
Encoders.
"""

from __future__ import unicode_literals

import os
import shlex
import logging
import subprocess

from django.utils.module_loading import import_by_path

from converter.ffmpeg import FFMpeg, FFMpegError, FFMpegConvertError

from encode import EncodeError
from encode.conf import settings


logger = logging.getLogger(__name__)


def get_encoder_class(import_path=None):
    """
    Get the encoder class by supplying a fully qualified path to
    ``import_path``.

    If ``import_path`` is ``None`` the default encoder class specified in the
    :py:data:`~encode.conf.ENCODE_DEFAULT_ENCODER_CLASS` is returned.

    :param import_path: Fully qualified path of the encoder class, for example:
        ``encode.encoders.BasicEncoder``.
    :type import_path: str

    :returns: The encoder class.
    :rtype: class
    """
    return import_by_path(import_path or settings.ENCODE_DEFAULT_ENCODER_CLASS)


class BaseEncoder(object):
    """
    The base encoder.

    :param profile: The encoding profile that configures this encoder.
    :type profile: :py:class:`~encode.models.EncodingProfile`
    :param input_path:
    :type input_path: str
    :param output_path:
    :type output_path: str
    """
    def __init__(self, profile, input_path=None, output_path=None):
        self.profile = profile
        self.input_path = input_path
        self.output_path = output_path

    def _build_exception(self, error, command):
        """
        Build an :py:class:`~encode.EncodeError` and return it.

        :param error: The description of the error.
        :type error: str
        :param command: The command used to produce the error.
        :type command: str
        :rtype: :py:class:`~encode.EncodeError`
        """
        output = getattr(error, 'output', None)

        exc = EncodeError(error)
        exc.output = output
        exc.command = command

        logger.error('Command output: {}'.format(output))

        return exc

    @property
    def command(self):
        """
        The command for the encoder with the vars injected, eg.
        ``convert "/path/to/input.gif" "/path/to/output.png"``.

        :rtype: str
        :returns: The command.
        """
        args = {
            "input": self.input_path,
            "output": self.output_path
        }

        return str(self.profile.encode_cmd.format(**args))


class BasicEncoder(BaseEncoder):
    """
    Encoder that uses the :py:mod:`subprocess` module.
    """
    def start(self):
        """
        Start encoding.

        :raises: :py:exc:`~encode.EncodeError` if something goes wrong
            during encoding.
        """
        command = shlex.split(self.command)

        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)

        except OSError as error:
            if error.errno == os.errno.ENOENT:
                # program not found
                exc = self._build_exception("{}: {}".format(
                    command[0], str(error)), self.command)
            else:
                exc = self._build_exception(str(error), self.command)
            raise exc

        except subprocess.CalledProcessError as error:
            exc = self._build_exception(error, self.command)
            raise exc


class FFMpegEncoder(BaseEncoder):
    """
    Encoder that uses the `FFMpeg <https://ffmpeg.org>`_ tool.
    """
    def start(self):
        """
        Start encoding.

        :raises: :py:exc:`~encode.EncodeError` if something goes wrong
            during encoding.
        """
        command = shlex.split(self.profile.command)

        try:
            ffmpeg = FFMpeg(self.profile.encoder.path)
            job = ffmpeg.convert(self.input_path, self.output_path, command)
            for timecode in job:
                logger.debug("Encoding (time: %f)...\r" % timecode)

        except FFMpegError as error:
            exc = self._build_exception(error, self.profile.command)
            raise exc

        except FFMpegConvertError as error:
            exc = self._build_exception(error.details, self.profile.command)
            raise exc
