# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import queued_storage.fields
import encode.storage
import encode.util
from django.conf import settings
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Encoder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name for this encoder. Example: FFmpeg', max_length=255, verbose_name='Name')),
                ('description', models.TextField(help_text='Optional description for this encoder.', null=True, verbose_name='Description', blank=True)),
                ('documentation_url', models.URLField(help_text='URL for the external documentation of this encoder.', max_length=255, null=True, verbose_name='Documentation URL', blank=True)),
                ('path', models.CharField(help_text='Name or path of the encoder executable. Example: /usr/local/bin/ffmpeg', max_length=255, verbose_name='Path')),
                ('klass', models.CharField(help_text='Optional encoder class to use. Example: encode.encoders.FFMpegEncoder', max_length=255, null=True, verbose_name='Class', blank=True)),
                ('command', models.CharField(help_text='Optional command options that are always added. Example: -loglevel fatal -y', max_length=255, null=True, verbose_name='Command', blank=True)),
                ('created_at', models.DateTimeField(help_text='The date and time the encoder was created.', verbose_name='Created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(help_text='The date and time the encoder was last modified.', verbose_name='Modified at', auto_now=True)),
            ],
            options={
                'verbose_name': 'Encoder',
                'verbose_name_plural': 'Encoders',
            },
        ),
        migrations.CreateModel(
            name='EncodingProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Title for this encoding profile. Example: WebM', max_length=255, verbose_name='Name')),
                ('description', models.TextField(help_text='Optional description for this encoding profile.', null=True, verbose_name='Description', blank=True)),
                ('mime_type', models.CharField(help_text='MIME-type for this encoding profile. Example: video/webm', max_length=255, null=True, verbose_name='MIME-type', blank=True)),
                ('container', models.CharField(help_text='Media container (file extension). Example: webm', max_length=50, verbose_name='Container')),
                ('video_codec', models.CharField(help_text='Video codec name. Example: VP8', max_length=255, null=True, verbose_name='Video Codec', blank=True)),
                ('audio_codec', models.CharField(help_text='Audio codec name. Example: Vorbis', max_length=255, null=True, verbose_name='Audio Codec', blank=True)),
                ('command', models.TextField(help_text='The command to execute, excluding the encoder executable\'s path or name. Supports variable interpolation. Example: -i "{input}" -acodec libvorbis -ab 128k -vcodec libvpx -s 320x240 "{output}"', verbose_name='Command')),
                ('created_at', models.DateTimeField(help_text='The date and time the profile was created.', verbose_name='Created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(help_text='The date and time the profile was last modified.', verbose_name='Modified at', auto_now=True)),
                ('encoder', models.ForeignKey(to='encode.Encoder', help_text='Encoder for this profile.', null=True)),
            ],
            options={
                'ordering': ['-name'],
                'verbose_name': 'Encoding profile',
                'verbose_name_plural': 'Encoding profiles',
            },
        ),
        migrations.CreateModel(
            name='MediaBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Title for this object.', max_length=255, verbose_name='Title')),
                ('file_type', models.CharField(max_length=255, verbose_name='File type', choices=[('audio', 'Audio'), ('video', 'Video'), ('snapshot', 'Snapshot')])),
                ('input_file', queued_storage.fields.QueuedFileField(storage=encode.storage.QueuedEncodeSystemStorage(), upload_to=encode.util.get_media_upload_to, blank=True, help_text='The uploaded source file.', null=True, verbose_name='Input file')),
                ('uploaded', models.BooleanField(default=False, help_text='Indicates that the output file(s) have been uploaded.', verbose_name='Uploaded', editable=False)),
                ('encoded', models.BooleanField(default=False, help_text='Indicates that the input file has finished encoding.', verbose_name='Encoded', editable=False)),
                ('encoding', models.BooleanField(default=False, help_text='Indicates that the input file is currently encoding.', verbose_name='Encoding', editable=False)),
                ('keep_input_file', models.BooleanField(default=False, help_text="Indicates that the input file should be saved and not\n            be removed after it's encoded and uploaded.", verbose_name='Keep input file')),
                ('created_at', models.DateTimeField(help_text='The date and time the object was created.', verbose_name='Created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(help_text='The date and time the object was last modified.', verbose_name='Modified at', auto_now=True)),
            ],
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'Media File',
                'verbose_name_plural': 'Media Files',
            },
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Title for this file.', max_length=255, null=True, verbose_name='Title', blank=True)),
                ('file', models.FileField(help_text='File for this model.', storage=django.core.files.storage.FileSystemStorage(), upload_to=encode.util.get_media_upload_to)),
                ('created_at', models.DateTimeField(help_text='The date and time the file was created.', verbose_name='Created at', auto_now_add=True)),
                ('modified_at', models.DateTimeField(help_text='The date and time the file was last modified.', verbose_name='Modified at', auto_now=True)),
            ],
            options={
                'verbose_name': 'Media file',
                'verbose_name_plural': 'Media files',
            },
        ),
        migrations.CreateModel(
            name='Audio',
            fields=[
                ('mediabase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='encode.MediaBase')),
            ],
            options={
                'verbose_name': 'Audio Clip',
                'verbose_name_plural': 'Audio Clips',
            },
            bases=('encode.mediabase',),
        ),
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('mediabase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='encode.MediaBase')),
            ],
            options={
                'verbose_name': 'Snapshot',
                'verbose_name_plural': 'Snapshots',
            },
            bases=('encode.mediabase',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('mediabase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='encode.MediaBase')),
            ],
            options={
                'verbose_name': 'Video Clip',
                'verbose_name_plural': 'Video Clips',
            },
            bases=('encode.mediabase',),
        ),
        migrations.AddField(
            model_name='mediabase',
            name='output_files',
            field=models.ManyToManyField(related_name='encoding_profiles', to='encode.MediaFile', blank=True, help_text='The encoded output file(s). Stored in CDN.', null=True, verbose_name='Output files'),
        ),
        migrations.AddField(
            model_name='mediabase',
            name='profiles',
            field=models.ManyToManyField(help_text='The encoding profile(s).', related_name='encoding_profiles', null=True, verbose_name='Encoding profiles', to='encode.EncodingProfile'),
        ),
        migrations.AddField(
            model_name='mediabase',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, help_text='The user who uploaded the input file.', null=True),
        ),
    ]
