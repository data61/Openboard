# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-07 03:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coag_uploader', '0003_auto_20160705_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='QualificationsData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.SmallIntegerField(choices=[(1, 'NSW'), (2, 'Vic'), (3, 'Qld'), (4, 'WA'), (5, 'SA'), (6, 'Tas'), (7, 'ACT'), (8, 'NT'), (100, 'Australia')])),
                ('year', models.SmallIntegerField()),
                ('financial_year', models.BooleanField()),
                ('percentage', models.DecimalField(decimal_places=1, max_digits=3)),
                ('uncertainty', models.DecimalField(decimal_places=1, max_digits=3)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='qualificationsdata',
            unique_together=set([('state', 'year')]),
        ),
    ]
