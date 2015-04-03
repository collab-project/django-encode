# -*- coding: utf-8 -*-
# Copyright Collab 2013-2015

"""
Tests for the :py:mod:`encode.encoders` module.
"""

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from django_webtest import WebTest

from encode import encoders, models, EncodeError
from encode.tests.helpers import DummyDataMixin


class GetEncoderClassTestCase(WebTest):
    """
    Tests for :py:func:`encode.encoders.get_encoder_class`.
    """
    def test_default(self):
        """
        Calling the function without any parameters returns the default
        encoder class.
        """
        klass = encoders.get_encoder_class()

        self.assertEqual(klass, encoders.BasicEncoder)

    def test_custom(self):
        """
        Get a custom encoder class.
        """
        klass = encoders.get_encoder_class('encode.encoders.FFMpegEncoder')

        self.assertEqual(klass, encoders.FFMpegEncoder)

    def test_none(self):
        """
        Retrieving a non-existing class raises an exception.
        """
        module_path = 'does.not.Exist'
        try:
            # django >= 1.7
            from django.utils.module_loading import import_string
            exception = ImportError
        except:
            exception = ImproperlyConfigured
        self.assertRaises(exception, encoders.get_encoder_class, module_path)


class BasicEncoderTestCase(WebTest, DummyDataMixin):
    """
    Tests for :py:class:`encode.encoders.BasicEncoder`.
    """
    def setUp(self):
        self.enc = models.Encoder.objects.get_or_create(name="convert",
            path="convert")[0]

        self.profile = models.EncodingProfile(name="Fake Profile")
        self.profile.command = "{input} {output}"
        self.profile.encoder = self.enc
        self.profile.save()

    def test_missingProgram(self):
        """
        An :py:class:`encode.EncodeError` is raised when the path to the
        encoder program cannot be found.
        """
        self.enc.path = "/fake/path/to/program"
        self.enc.save()

        encoder = encoders.BasicEncoder(self.profile, 'foo', 'bar')

        with self.assertRaises(EncodeError) as cm:
            encoder.start()

        self.assertTrue(str(cm.exception).startswith(
            '{}: [Errno 2] No such file or directory'.format(self.enc.path)))

        self.assertEqual(cm.exception.command,
            "{} foo bar".format(self.enc.path))

    def test_badParameters(self):
        """
        An :py:class:`encode.EncodeError` is raised when the encoder receives
        unknown parameters.
        """
        encoder = encoders.BasicEncoder(self.profile, 'foo', 'bar')

        with self.assertRaises(EncodeError) as cm:
            encoder.start()

        self.assertEqual(str(cm.exception),
            "Command '['convert', 'foo', 'bar']' returned non-zero "
            "exit status 1")
        self.assertEqual(cm.exception.command, "convert foo bar")

    def test_baseCommand(self):
        """
        Extra command options are added to every job.
        """
        self.enc.command = '-loglevel fatal -y'
        self.enc.save()

        self.assertEqual(self.enc.encode_cmd,
            ['convert', '-loglevel', 'fatal', '-y'])


class FFMpegEncoderTestCase(WebTest, DummyDataMixin):
    """
    Tests for :py:class:`encode.encoders.FFMpegEncoder`.
    """
    def setUp(self):
        self.enc = models.Encoder.objects.get_or_create(name="ffmpeg",
            path="ffmpeg")[0]

        self.profile = models.EncodingProfile(name="Fake Profile")
        self.profile.command = "{input} {output}"
        self.profile.encoder = self.enc
        self.profile.save()

    def test_missingProgram(self):
        """
        An :py:class:`encode.EncodeError` is raised when the FFmpeg
        executable cannot be found.
        """
        self.enc.path = "/fake/path/to/ffmpeg"
        self.enc.save()

        encoder = encoders.FFMpegEncoder(self.profile, 'foo', 'bar')

        with self.assertRaises(EncodeError) as cm:
            encoder.start()

        self.assertEqual(str(cm.exception),
            'ffmpeg binary not found: /fake/path/to/ffmpeg')
        self.assertEqual(cm.exception.command, self.profile.command)

    def test_missingInputfile(self):
        """
        An :py:class:`encode.EncodeError` is raised when the encoder cannot
        find the input file.
        """
        encoder = encoders.FFMpegEncoder(self.profile, 'foo', 'bar')

        with self.assertRaises(EncodeError) as cm:
            encoder.start()

        self.assertEqual(str(cm.exception), "Input file doesn't exist: foo")
        self.assertEqual(cm.exception.command, self.profile.command)

    def test_invalidInputfile(self):
        """
        An :py:class:`encode.EncodeError` is raised when the encoder cannot
        convert the input file because it doesn't contain valid media data.
        """
        encoder = encoders.FFMpegEncoder(self.profile, __file__, 'bar')

        self.assertRaises(EncodeError, encoder.start)
