# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-17 01:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0057_geowindow_view_override'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphcluster',
            name='dynamic_label',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='graphdataset',
            name='dynamic_label',
            field=models.BooleanField(default=False),
        ),
    ]
