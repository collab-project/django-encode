# Copyright Collab 2014-2015

"""
Forms.
"""

from __future__ import unicode_literals

from django import forms

from encode import models
from encode.widgets import MediaDisplayWidget


class SnapshotAdminForm(forms.ModelForm):
    """
    Admin form for :py:class:`encode.models.Snapshot` models.
    """
    class Meta:
        model = models.Snapshot
        exclude = ()
        widgets = {
            'output_files': MediaDisplayWidget
        }


class AudioAdminForm(forms.ModelForm):
    """
    Admin form for :py:class:`encode.models.Audio` models.
    """
    class Meta:
        model = models.Audio
        exclude = ()
        widgets = {
            'output_files': MediaDisplayWidget
        }


class VideoAdminForm(forms.ModelForm):
    """
    Admin form for :py:class:`encode.models.Video` models.
    """
    class Meta:
        model = models.Video
        exclude = ()
        widgets = {
            'output_files': MediaDisplayWidget
        }
