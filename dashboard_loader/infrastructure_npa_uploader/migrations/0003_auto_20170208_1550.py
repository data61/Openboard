# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-08 04:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure_npa_uploader', '0002_auto_20170208_1352'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='infrastructurekeyprojects',
            options={'ordering': ('state', 'project')},
        ),
    ]
