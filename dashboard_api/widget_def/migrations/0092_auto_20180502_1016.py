# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-02 00:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0091_auto_20170807_1129'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='widgetview',
            unique_together=set([('parent', 'sort_order'), ('parent', 'name')]),
        ),
    ]
