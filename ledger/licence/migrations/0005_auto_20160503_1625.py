# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-03 08:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licence', '0004_auto_20160503_1145'),
    ]

    operations = [
        migrations.RenameField(
            model_name='licencetype',
            old_name='description',
            new_name='statement',
        ),
        migrations.AddField(
            model_name='licencetype',
            name='act',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='licencetype',
            name='authority',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
