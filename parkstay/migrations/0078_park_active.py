# Generated by Django 3.2.4 on 2021-09-24 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0077_park_alert_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
