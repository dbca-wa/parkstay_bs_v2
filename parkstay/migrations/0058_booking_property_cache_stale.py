# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-26 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0057_booking_property_cache_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='property_cache_stale',
            field=models.BooleanField(default=True),
        ),
    ]