# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-22 03:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['user']},
        ),
    ]
