# Generated by Django 3.2.18 on 2023-08-07 02:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0136_mybookingnotices_notices'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MyBookingNotices',
            new_name='MyBookingNotice',
        ),
        migrations.RenameModel(
            old_name='Notices',
            new_name='Notice',
        ),
    ]
