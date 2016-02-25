# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-07 19:08
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.datetime_safe


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(db_index=True, max_length=129, unique=True)),
                ('name', models.CharField(blank=True, max_length=60)),
                ('email', models.CharField(blank=True, max_length=254)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=10)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('profile_image', models.CharField(blank=True, max_length=256)),
                ('profile_background_image', models.CharField(blank=True, max_length=256)),
                ('profile_message', models.CharField(blank=True, max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('social', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Couple',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('coupling_begin', models.DateField(default=django.utils.datetime_safe.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='DatePost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=100)),
                ('message', models.CharField(max_length=1000)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), db_index=True, size=None)),
                ('photos', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=256), size=None)),
                ('couple', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apiserver.Couple')),
            ],
        ),
        migrations.CreateModel(
            name='DatePostComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('datepost', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apiserver.DatePost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='couple',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apiserver.Couple'),
        ),
    ]
