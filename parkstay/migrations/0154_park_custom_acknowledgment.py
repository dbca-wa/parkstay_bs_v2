from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0153_bulkrefundcancellist_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='custom_acknowledgment',
            field=models.TextField(
                blank=True, default='',
                help_text='If set, users must check this acknowledgment before proceeding with a booking.'
            ),
        ),
    ]
