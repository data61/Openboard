# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 01:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0088_auto_20170301_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphdisplayoptions',
            name='pie',
            field=models.SmallIntegerField(choices=[(0, b'circle'), (1, b'ring'), (2, b'linear_horizontal'), (3, b'linear_vertical'), (4, b'patchwork')], default=0, help_text=b'For pie charts, how to display the pie(s)'),
        ),
    ]
