# Copyright Collab 2014-2015

"""
Tests for the :py:mod:`encode.models` module.
"""

from __future__ import unicode_literals

from django.core.files.base import ContentFile

from encode.models import Audio, Video, EncodingProfile
from encode.tests.helpers import WEBM_DATA, FileTestCase


class MediaBaseTestCase(FileTestCase):
    """
    Tests for the :py:class:`encode.models.MediaBase` model.
    """
    def test_get_media(self):
        """
        `get_media` returns an instance of the model.
        """
        afile = Audio.objects.create(title='Foo')

        self.assertEqual(repr(afile.get_media()), '<Audio: Foo>')

    def test_badProfileIds(self):
        """
        Passing non-existent encoding profile id's to `save()`
        raises an error.
        """
        title = 'test.webm'
        vfile = Video.objects.create(title='Foo')

        # attach file to model
        data = ContentFile(WEBM_DATA, title)

        # store file data but don't save related model until
        # the encoding profiles are saved as well
        getattr(vfile, 'input_file').save(title, data, save=False)

        self.assertRaises(EncodingProfile.DoesNotExist, vfile.save,
            profiles=[18])
