# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-22 06:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apiserver', '0002_auto_20160222_0048'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatePostMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('message', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=10)),
                ('data', models.CharField(blank=True, max_length=256)),
                ('datepost', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apiserver.DatePost')),
            ],
        ),
    ]
