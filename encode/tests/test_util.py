# -*- coding: utf-8 -*-
# Copyright Collab 2013-2015

"""
Tests for the :py:mod:`encode.util` module.
"""

from __future__ import unicode_literals

import os

from django_webtest import WebTest

from encode.conf import settings
from encode.tests import helpers

from encode import models, util, DecodeError, VIDEO, EncodeError, get_version


class GetRandomFileNameTestCase(WebTest):
    """
    Tests for :py:func:`encode.util.get_random_filename`.
    """
    def test_basic(self):
        """
        Calling the function without any parameters returns a filename with
        12 characters and the extension '.png'.
        """
        fn = util.get_random_filename()

        self.assertTrue(fn.endswith('.png'))
        self.assertEqual(len(fn), 16)

    def test_length(self):
        """
        Calling the function with a character total of 4 and the extension
        '.gif' returns a valid filename.
        """
        fn = util.get_random_filename('gif', 4)

        self.assertTrue(fn.endswith('.gif'))
        self.assertEqual(len(fn), 8)


class FqnTestCase(WebTest):
    """
    Tests for :py:func:`encode.util.fqn`.
    """
    def test_class(self):
        """
        Passing a class instance to `fqn` returns the fully qualified name.
        """
        result = util.fqn(self)
        self.assertEqual(result, 'encode.tests.test_util.FqnTestCase')


class GetMediaUploadToTestCase(WebTest):
    """
    Tests for :py:func:`encode.util.get_media_upload_to`.
    """
    def test_basic(self):
        """
        Passing an object instance with a filename returns a pathname.
        """
        result = util.get_media_upload_to(object(), 'foo.png')
        self.assertEqual(result, 'encode_test/files/foo.png')

    def test_instance(self):
        """
        Passing an object instance, that has a `file_type` attribute, with a
        filename returns a pathname.
        """
        class DummyFile(object):
            file_type = VIDEO

        result = util.get_media_upload_to(DummyFile(), 'foo.mp4')
        self.assertEqual(result, 'encode_test/video/foo.mp4')


class ParseMediaTestCase(WebTest):
    """
    Tests for :py:func:`encode.util.parseMedia`.
    """
    def test_goodData(self):
        """
        Passing base64-encoded data to `parseMedia` returns a decoded
        string.
        """
        webm = util.parseMedia(helpers.WEBM_DATA)
        self.assertEqual(len(webm), 923)

        wav = util.parseMedia(helpers.WAV_DATA)
        self.assertEqual(len(wav), 6122)

        png = util.parseMedia(helpers.PNG_DATA)
        self.assertEqual(len(png), 218)

    def test_badData(self):
        """
        Passing corrupt or unsupported data to `parseMedia` raises a
        :py:class:`~encode.DecodeError`.
        """
        self.assertRaises(DecodeError, util.parseMedia, 'foo')
        self.assertRaises(DecodeError, util.parseMedia, {})
        self.assertRaises(DecodeError, util.parseMedia, [])
        self.assertRaises(DecodeError, util.parseMedia, ())


class VersionTestCase(WebTest):
    """
    Tests for :py:mod:`~encode` versioning information.
    """
    def test_regularVersion(self):
        """
        :py:func:`~encode.get_version` returns a string version without
        any beta tags, eg. `1.0.1`.
        """
        version = (1, 0, 1)
        self.assertEqual(get_version(version), '1.0.1')

    def test_betaVersion(self):
        """
        :py:func:`~encode.get_version` returns a string version with beta tags,
        eg. `1.2.3b1`.
        """
        version = (1, 2, 3, 'b1')
        self.assertEqual(get_version(version), '1.2.3b1')


class TemporaryMediaFileTestCase(helpers.FileTestCase, helpers.DummyDataMixin):
    """
    Tests for :py:class:`encode.util.TemporaryMediaFile`.
    """
    def setUp(self):
        helpers.DummyDataMixin.setUp(self)
        helpers.FileTestCase.setUp(self)

    def assertFiles(self, result, expected=[]):
        """
        Verify the input file's gone and the expected number of output
        files is correct.
        """
        inputFile = getattr(result, self.inputFileField).file.name
        self.assertFalse(os.path.exists(inputFile))

        outputFiles = getattr(result, 'output_files').all()
        self.assertEqual(len(outputFiles), len(expected))

        for index, fileObj in enumerate(outputFiles):
            fileName = fileObj.file.name
            extension = expected[index]
            self.assertTrue(fileName.endswith(extension),
                "{} does not have the extension '{}'".format(fileName,
                extension))

    def test_singleProfile(self):
        """
        Encoding a file with a single profile results in one output file.
        """
        result = self.createTempFile('img_', models.Snapshot,
            settings.ENCODE_IMAGE_PROFILES,
            helpers.PNG_DATA)

        self.assertFiles(result, ['.png'])

    def test_badProfile(self):
        """
        Encoding a file with a non-existing encoding profile raises a
        :py:class:`encode.EncodeError`.
        """
        unknown_profiles = ['bad']
        self.assertRaises(EncodeError, self.createTempFile, 'bad_', models.Snapshot,
            unknown_profiles, helpers.PNG_DATA)

    def test_multipleProfiles(self):
        """
        Encoding a file with multiple profiles results in multiple output
        files.
        """
        result = self.createTempFile('video_', models.Video,
            settings.ENCODE_VIDEO_PROFILES,
            helpers.WEBM_DATA)

        self.assertFiles(result, ['.webm', '.mp4'])
