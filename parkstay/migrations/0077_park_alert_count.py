# Generated by Django 3.2.4 on 2021-09-24 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0076_alter_campgroundnotice_notice_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='alert_count',
            field=models.IntegerField(default=0),
        ),
    ]
