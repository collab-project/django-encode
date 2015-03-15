# -*- coding: utf-8 -*-
# Copyright Collab 2014-2015

"""
Tests for the :py:mod:`encode.admin` module.
"""

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.admin.sites import AdminSite

from webtest import Upload

from django_webtest import WebTest

from encode import admin, models
from encode.util import get_random_filename, parseMedia
from encode.tests.helpers import PNG_DATA, DummyDataMixin, FileTestCase


class MockRequest(object):
    pass

request = MockRequest()


class MediaFileAdminTests(WebTest):
    """
    Tests for :py:class:`encode.admin.MediaFileAdmin`.
    """
    def setUp(self):
        self.mfile = models.MediaFile.objects.create(
            title='The Doors'
        )
        self.site = AdminSite()

    def test_fields(self):
        ma = admin.MediaFileAdmin(models.MediaFile, self.site)

        self.assertEqual(list(ma.get_form(request).base_fields),
            ['title', 'file'])
        self.assertEqual(ma.search_fields, ['title'])
        self.assertEqual(ma.ordering, ['title'])

    def test_repr(self):
        """
        `repr()` for the model includes the `title` attribute.
        """
        self.assertEqual(repr(self.mfile), '<MediaFile: The Doors>')


class EncoderAdminTests(WebTest):
    """
    Tests for :py:class:`encode.admin.EncoderAdmin`.
    """
    def setUp(self):
        self.enc = models.Encoder.objects.get_or_create(
            name="convert", path="convert"
        )
        self.site = AdminSite()

    def test_fields(self):
        ma = admin.EncoderAdmin(models.Encoder, self.site)

        self.assertEqual(list(ma.get_form(request).base_fields),
            ['name', 'description', 'documentation_url', 'path', 'klass',
             'command'])
        self.assertEqual(ma.search_fields, ['name', 'description'])
        self.assertEqual(ma.ordering, ['name'])
        self.assertEqual(ma.list_display, ('name', 'path', 'command', 'klass'))
        self.assertEqual(ma.list_filter, ('name', 'path'))


class EncodingProfileAdminTests(WebTest):
    """
    Tests for :py:class:`encode.admin.EncodingProfileAdmin`.
    """
    def setUp(self):
        self.enc = models.Encoder.objects.create(
            name="convert", path="convert")

        self.profile = models.EncodingProfile(name="Fake Profile")
        self.profile.command = "{input} {output}"
        self.profile.encoder = self.enc
        self.profile.save()
        self.site = AdminSite()
        self.ma = admin.EncodingProfileAdmin(models.EncodingProfile, self.site)

    def test_fields(self):
        self.assertEqual(list(self.ma.get_form(request).base_fields),
            ['name', 'description', 'mime_type', 'container', 'video_codec',
             'audio_codec', 'encoder', 'command'])
        self.assertEqual(self.ma.search_fields, ['name', 'description',
             'mime_type', 'container'])
        self.assertEqual(self.ma.ordering, ['name'])
        self.assertEqual(self.ma.list_display, ('name', 'encoder_link',
             'container', 'mime_type', 'video_codec', 'audio_codec'))
        self.assertEqual(self.ma.list_filter, ('container', 'mime_type',
            'encoder'))

    def test_encoder_link(self):
        self.assertHTMLEqual(self.ma.encoder_link(self.profile),
            "<b><a href='/encode/encoder/{}/'>{}</a></b>".format(
            self.profile.id, self.profile.encoder.name))


class MediaAdminTests(FileTestCase, DummyDataMixin):
    """
    Tests for :py:class:`encode.admin.MediaAdmin`.
    """
    def setUp(self):
        DummyDataMixin.setUp(self)
        FileTestCase.setUp(self)

        self.site = AdminSite()
        self.ma = admin.MediaAdmin(models.Snapshot, self.site)

    def test_fields(self):
        self.assertEqual(list(self.ma.get_form(request).base_fields),
            ['title', 'input_file', 'keep_input_file', 'profiles',
            'output_files'])
        self.assertEqual(self.ma.exclude, ('user', 'file_type'))
        self.assertEqual(self.ma.ordering, ['-modified_at'])
        self.assertEqual(self.ma.list_display_links, ('title',))
        self.assertEqual(self.ma.list_display, ('title', 'encoded',
             'uploaded', 'created_at', 'modified_at'))
        self.assertEqual(self.ma.list_filter, ('encoded', 'profiles',
            'uploaded'))
        self.assertEqual(self.ma.readonly_fields, ('encoded', 'uploaded'))

    def test_save_model(self):
        user = User.objects.create_superuser('thijs', 'foo@example.com',
            'secret')
        url = reverse('admin:encode_snapshot_add')
        response = self.app.get(url, user=user)

        # fill in and submit form
        response.form['title'] = 'foo'
        response.form['input_file'] = Upload(
            get_random_filename('png'), parseMedia(PNG_DATA))
        response.form['profiles'].force_value(['8'])
        response = response.form.submit().follow(status=200)
