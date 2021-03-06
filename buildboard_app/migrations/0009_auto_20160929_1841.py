# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-29 18:41
from __future__ import unicode_literals

import buildboard_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildboard_app', '0008_auto_20160922_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(upload_to=buildboard_app.models.get_logo_path),
        ),
        migrations.AlterField(
            model_name='project',
            name='team_photo',
            field=models.ImageField(upload_to=buildboard_app.models.get_team_photo_path),
        ),
    ]
