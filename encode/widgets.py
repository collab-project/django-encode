# Copyright Collab 2014-2015

"""
Widgets.
"""

from __future__ import unicode_literals

from itertools import chain

from django import forms
from django.utils.safestring import mark_safe


class MediaDisplayWidget(forms.SelectMultiple):
    """
    Widget for displaying media in admin forms.
    """

    class Media:
        js = ("encode/js/media.js",)

    def render(self, name, value, attrs=None, choices=()):
        paths = []
        script = ''

        if value is not None:
            for option_value, option_label in chain(self.choices, choices):
                if option_value in [int(x) for x in value]:
                    try:
                        from encode import models
                        path = models.MediaFile.objects.get(title=option_label).file.url
                        paths.append(path)
                    except models.MediaFile.DoesNotExist:
                        pass

            script = '''<script type="text/javascript">
                $(document).ready(function() {
                    var elem = $('#id_%(name)s');
                    var widget = new collab.PreviewWidget(elem, %(paths)s);
                });
                </script>''' % {'name': name, 'paths': paths}

        if attrs is None:
            attrs = {}

        output = super(MediaDisplayWidget, self).render(name, value, attrs,
                                                       choices)

        return mark_safe(output + script)
