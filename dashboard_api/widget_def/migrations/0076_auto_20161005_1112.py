# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-05 00:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0075_auto_20160929_1429'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parametisationvalue',
            options={'ordering': ('param', 'id')},
        ),
    ]
