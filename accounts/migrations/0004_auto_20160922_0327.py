# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-22 03:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20160922_0324'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['user']},
        ),
    ]