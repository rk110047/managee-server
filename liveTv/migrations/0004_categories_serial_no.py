# Generated by Django 3.0 on 2020-08-19 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveTv', '0003_channels_catchup_recording_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='categories',
            name='serial_no',
            field=models.IntegerField(default=0),
        ),
    ]
