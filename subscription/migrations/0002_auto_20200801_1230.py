# Generated by Django 3.0 on 2020-08-01 12:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='individualsubscriptiondevices',
            options={},
        ),
        migrations.AlterModelOptions(
            name='subscriptionpackagedevices',
            options={},
        ),
        migrations.RenameField(
            model_name='subscriptionpackagedevices',
            old_name='subscription_package',
            new_name='package',
        ),
        migrations.RemoveField(
            model_name='devicetype',
            name='device_name',
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='device_type',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='individualsubscriptiondevices',
            unique_together={('user', 'device')},
        ),
        migrations.AlterUniqueTogether(
            name='subscriptionpackagedevices',
            unique_together={('package', 'device')},
        ),
        migrations.CreateModel(
            name='UserActiveSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('mac_address', models.CharField(max_length=30, unique=True)),
                ('device_name', models.CharField(max_length=50)),
                ('device_model', models.CharField(max_length=50)),
                ('location', models.CharField(blank=True, max_length=20, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscription.DeviceType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserSubscriptionPackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscription.SubscriptionPackage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'package')},
            },
        ),
    ]