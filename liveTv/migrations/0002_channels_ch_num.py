# Generated by Django 3.0 on 2020-07-05 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveTv', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channels',
            name='ch_num',
            field=models.IntegerField(default=0),
        ),
    ]