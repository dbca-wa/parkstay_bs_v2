# Generated by Django 3.2.4 on 2021-10-15 07:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0083_bookingpolicy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingpolicy',
            name='peak_grace_time',
            field=models.PositiveIntegerField(blank=True, default=10080, null=True),
        ),
        migrations.AlterField(
            model_name='bookingpolicy',
            name='peak_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='peak_group_policy', to='parkstay.peakgroup'),
        ),
        migrations.AlterField(
            model_name='bookingpolicy',
            name='peak_policy_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bookingpolicy',
            name='peak_policy_type',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Per Day'), (1, 'Fixed Fee'), (2, 'Booking Percentage')], default=0, null=True),
        ),
    ]
