# Copyright Collab 2012-2015

"""
Admin functionality.
"""

from __future__ import unicode_literals

from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from encode import models, forms


class MediaFileAdmin(admin.ModelAdmin):
    """
    Admin definition for :py:class:`encode.models.MediaFile` models.
    """
    list_display = ('title', 'created_at',)
    ordering = ['title']
    search_fields = ['title']


class EncoderAdmin(admin.ModelAdmin):
    """
    Admin definition for :py:class:`encode.models.Encoder` models.
    """
    ordering = ['name']
    search_fields = ['name', 'description']
    list_filter = ('name', 'path',)
    list_display = ('name', 'path', 'command', 'klass')


class EncodingProfileAdmin(admin.ModelAdmin):
    """
    Admin definition for :py:class:`encode.models.EncodingProfile` models.
    """
    list_display = ('name', 'encoder_link', 'container', 'mime_type',
                    'video_codec', 'audio_codec')
    ordering = ['name']
    search_fields = ['name', 'description', 'mime_type', 'container']
    list_filter = ('container', 'mime_type', 'encoder',)

    def encoder_link(self, obj):
        markup = "<b><a href='{url}'>{name}</a></b>"
        url = reverse('admin:encode_encoder_change', args=(
            obj.encoder.id,))
        return markup.format(name=obj.encoder.name, url=url)

    encoder_link.short_description = _('Encoder')
    encoder_link.allow_tags = True


class MediaAdmin(admin.ModelAdmin):
    """
    Base admin for media objects.
    """
    list_display = ('title', 'encoded', 'uploaded', 'created_at',
                    'modified_at')
    list_display_links = ('title',)
    exclude = ('user', 'file_type',)
    readonly_fields = ('encoded', 'uploaded')
    list_filter = ('encoded', 'profiles', 'uploaded',)
    ordering = ['-modified_at']
    filter_horizontal = ('profiles',)

    def save_model(self, request, obj, form, change):
        """
        Attaches the ``user`` to the media object and displays a success
        notification message in the admin interface.

        Called when the :py:class:`encode.tasks.EncodeMedia` task completed.
        """
        obj.user = request.user

        messages.success(request,
            _("The file is being encoded."))

        # The `profiles` m2m field does not get stored in the model until it's
        # properly saved, and our tasks need the profile(s) in order to encode
        # the file, so pass them to `encode.models.MediaBase.save()`
        profiles = request.POST.getlist('profiles')

        obj.save(profiles=profiles)


class VideoAdmin(MediaAdmin):
    """
    Admin for :py:class:`encode.models.Video` models.
    """
    form = forms.VideoAdminForm


class AudioAdmin(MediaAdmin):
    """
    Admin for :py:class:`encode.models.Audio` models.
    """
    form = forms.AudioAdminForm


class SnapshotAdmin(MediaAdmin):
    """
    Admin for :py:class:`encode.models.Snaphot` models.
    """
    form = forms.SnapshotAdminForm


admin.site.register(models.MediaFile, MediaFileAdmin)
admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.Audio, AudioAdmin)
admin.site.register(models.Snapshot, SnapshotAdmin)
admin.site.register(models.EncodingProfile, EncodingProfileAdmin)
admin.site.register(models.Encoder, EncoderAdmin)
