# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-01 22:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0081_auto_20170201_1435'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={'ordering': ['group', 'key'], 'verbose_name_plural': 'properties'},
        ),
    ]
