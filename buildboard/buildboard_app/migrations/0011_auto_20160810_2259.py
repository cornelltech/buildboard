# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-10 22:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildboard_app', '0010_auto_20160810_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(upload_to='static/uploads/logo/'),
        ),
    ]
