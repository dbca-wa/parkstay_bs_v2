# Generated by Django 3.2.4 on 2021-11-29 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0099_campground_campground_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkstayPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emailuser_id', models.IntegerField(blank=True, null=True)),
                ('permission_group', models.SmallIntegerField(choices=[(0, 'Multiple Campsite Selection')], default=0)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
