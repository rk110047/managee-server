# Generated by Django 3.0 on 2020-10-01 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0002_package_is_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='backgroundImage_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='package',
            name='discount',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='package',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='package',
            name='thumbnailImage_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='package',
            name='validity',
            field=models.DurationField(blank=True, null=True),
        ),
    ]