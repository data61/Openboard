# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-13 01:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0071_auto_20160912_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawdataset',
            name='filename',
            field=models.CharField(help_text=b"The filename for the generated csv file. (Should end in '.csv').", max_length=128),
        ),
        migrations.AlterField(
            model_name='rawdataset',
            name='name',
            field=models.CharField(help_text=b'A longer more descriptive name for the raw dataset. May be parametised.', max_length=128),
        ),
        migrations.AlterField(
            model_name='rawdataset',
            name='url',
            field=models.SlugField(help_text=b'A short symbolic label for the raw dataset, as used in the API', verbose_name=b'label'),
        ),
        migrations.AlterField(
            model_name='rawdataset',
            name='widget',
            field=models.ForeignKey(help_text=b'The Widget this dataset belongs to', on_delete=django.db.models.deletion.CASCADE, to='widget_def.WidgetDefinition'),
        ),
        migrations.AlterField(
            model_name='viewwidgetdeclaration',
            name='child_view',
            field=models.ForeignKey(blank=True, help_text=b'(Optional) The label of a view which can be navigated to through this widget.  Would typically be a child view of the containing view, or at least in the same navigation hierarchy, but this is not required.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='declarations', to='widget_def.WidgetView'),
        ),
        migrations.AlterField(
            model_name='viewwidgetdeclaration',
            name='child_view_text',
            field=models.CharField(blank=True, help_text=b'The text to display in the hyperlink pointing to the child view.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='viewwidgetdeclaration',
            name='definition',
            field=models.ForeignKey(help_text=b'The WidgetDefinition to include in the WidgetView', on_delete=django.db.models.deletion.CASCADE, to='widget_def.WidgetDefinition'),
        ),
        migrations.AlterField(
            model_name='viewwidgetdeclaration',
            name='sort_order',
            field=models.IntegerField(help_text=b'How the widget is to be sorted within the view'),
        ),
        migrations.AlterField(
            model_name='viewwidgetdeclaration',
            name='view',
            field=models.ForeignKey(help_text=b'The WidgetView the WidgetDefinition is to be included in', on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='widget_def.WidgetView'),
        ),
    ]
