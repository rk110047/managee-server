# Generated by Django 3.0 on 2020-08-19 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vod', '0002_auto_20200705_0914'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='serial_no',
            field=models.IntegerField(default=0),
        ),
    ]
