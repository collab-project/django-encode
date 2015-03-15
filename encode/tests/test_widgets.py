# Copyright Collab 2015

"""
Tests for the :py:mod:`encode.widgets` module.
"""

from __future__ import unicode_literals

from django.conf import settings

from encode.models import Video
from encode.widgets import MediaDisplayWidget
from encode.tests.helpers import WEBM_DATA, FileTestCase, DummyDataMixin


class WidgetTestCase(FileTestCase, DummyDataMixin):
    def setUp(self):
        DummyDataMixin.setUp(self)
        FileTestCase.setUp(self)

    def test_render_with_choices(self):
        widget = MediaDisplayWidget()

        self.assertEqual(
            '<select multiple="multiple" id="id_color" name="test">\n<option value="1" selected="selected">foo</option>\n<option value="2" selected="selected">bar</option>\n<option value="3">spam</option>\n</select><script type="text/javascript">\n                $(document).ready(function() {\n                    var elem = $(\'#id_test\');\n                    var widget = new collab.PreviewWidget(elem, []);\n                });\n                </script>',
            widget.render(
                name='test',
                value=[1, 2],
                attrs={'id': 'id_color'},
                choices=((1, "foo"), (2, "bar"), (3, "spam"))
            )
        )

    def test_render_without_choices(self):
        widget = MediaDisplayWidget()

        self.assertIn(
            '<select multiple="multiple" id="id_color" name="test">\n</select>',
            widget.render(
                name='test',
                value=[1, 2],
                attrs={'id': 'id_color'}
            )
        )

    def test_render_without_attrs(self):
        widget = MediaDisplayWidget()

        self.assertIn(
            '<select multiple="multiple" name="test">\n<option value="1" selected="selected">foo</option>\n<option value="2" selected="selected">bar</option>\n<option value="3">spam</option>\n</select>',
            widget.render(
                name='test',
                value=[1, 2],
                choices=((1, "foo"), (2, "bar"), (3, "spam"))
            )
        )

    def test_render_with_files(self):
        result = self.createTempFile('video_', Video,
            settings.ENCODE_VIDEO_PROFILES,
            WEBM_DATA)

        widget = MediaDisplayWidget()
        files = result.output_files.all()
        choices = [(x.id, x.title) for x in files]

        self.assertIn(
            '<select multiple="multiple" name="test">\n<option value="1" selected="selected">{}</option>\n<option value="2">{}</option>\n</select>'.format(
                files[0].title, files[1].title),
            widget.render(
                name='test',
                value=[files[0].id],
                choices=choices
            )
        )
