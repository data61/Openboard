# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-28 23:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0086_graphdataset_hide_from_legend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphdefinition',
            name='vertical_axis_buffer',
            field=models.DecimalField(decimal_places=0, default=b'0.0', max_digits=3),
        ),
    ]
