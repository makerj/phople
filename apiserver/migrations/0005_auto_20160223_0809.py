# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-22 23:09
from __future__ import unicode_literals

import apiserver.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiserver', '0004_auto_20160223_0403'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datepost',
            name='photos',
        ),
        migrations.AlterField(
            model_name='datepostmedia',
            name='data',
            field=apiserver.models.S3Field(keyform='datepostmedia/{}', max_length=256, size_limit=209715200),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_background_image',
            field=apiserver.models.S3Field(blank=True, keyform='profile_background_image/{}', max_length=256, null=True, size_limit=5242880),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=apiserver.models.S3Field(blank=True, keyform='profile_image/{}', max_length=256, null=True, size_limit=2097152),
        ),
    ]