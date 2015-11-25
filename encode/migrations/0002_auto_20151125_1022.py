# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('encode', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediabase',
            name='output_files',
            field=models.ManyToManyField(help_text='The encoded output file(s). Stored in CDN.', related_name='encoding_profiles', verbose_name='Output files', to='encode.MediaFile', blank=True),
        ),
        migrations.AlterField(
            model_name='mediabase',
            name='profiles',
            field=models.ManyToManyField(help_text='The encoding profile(s).', related_name='encoding_profiles', verbose_name='Encoding profiles', to='encode.EncodingProfile'),
        ),
    ]
