# -*- coding: utf-8 -*-
# Copyright Collab 2013-2015

"""
Tests for the :py:mod:`encode.tasks` module.
"""

from __future__ import unicode_literals

from django_webtest import WebTest

from encode import models, tasks, EncodeError, UploadError


class MediaBaseTestCase(WebTest):
    """
    Tests for :py:func:`encode.tasks.media_base`.
    """
    def test_doesNotExist(self):
        """
        `media_base` raises an error when a non-existing model id
        is passed.
        """
        self.assertRaises(models.MediaBase.DoesNotExist, tasks.media_base, 20)


class EncodeMediaTestCase(WebTest):
    """
    Tests for :py:class:`encode.tasks.EncodeMedia` task.
    """
    def test_encodeError(self):
        """
        `EncodeMedia` raises an :py:class:`encode.EncodeError` when
        something goes wrong.
        """
        encoder = models.Encoder.objects.create(name='testEncoder',
            path='/fake/path/testEncoder')
        profile = models.EncodingProfile(name='testProfile')
        profile.encoder = encoder
        profile.container = 'webm'
        profile.save()
        modelObj = models.Video.objects.create(title='testVideo')
        output_path = modelObj.output_path(profile)

        encode_media = tasks.EncodeMedia()
        self.assertRaises(EncodeError, encode_media.apply_async,
            args=[profile, modelObj.id, '/fake/inputPath', output_path])


class StoreMediaTestCase(WebTest):
    """
    Tests for :py:class:`encode.tasks.StoreMedia` task.
    """
    def test_uploadError(self):
        """
        `StoreMedia` raises an :py:class:`encode.UploadError` when
        something goes wrong.
        """
        profile = models.EncodingProfile.objects.create(name='testProfile',
            container='webm')
        modelObj = models.Video.objects.create(title='testVideo')
        data = {'id': modelObj.id, 'profile': profile}
        store_media = tasks.StoreMedia()

        self.assertRaisesMessage(UploadError,
            '{} does not exist'.format(modelObj.output_path(profile)),
            store_media.apply_async,
            args=[data])
