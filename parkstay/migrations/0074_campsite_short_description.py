# Generated by Django 3.2.4 on 2021-09-13 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0073_campgroundnotice'),
    ]

    operations = [
        migrations.AddField(
            model_name='campsite',
            name='short_description',
            field=models.TextField(blank=True, max_length=150, null=True),
        ),
    ]
