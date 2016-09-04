# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-21 04:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widget_data', '0018_auto_20160617_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphdata',
            name='err_valmax',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name='graphdata',
            name='err_valmin',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True),
        ),
    ]