# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-02 00:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health_agedcare_uploader', '0002_auto_20170210_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthagedcaredata',
            name='transitional',
            field=models.DecimalField(decimal_places=1, default='0.0', max_digits=5),
        ),
    ]
