from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0154_park_custom_acknowledgment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='park',
            name='custom_acknowledgment',
        ),
        migrations.AddField(
            model_name='campground',
            name='custom_acknowledgment',
            field=models.TextField(
                blank=True, default='',
                help_text='If set, users must check this acknowledgment before proceeding with a booking.'
            ),
        ),
    ]
