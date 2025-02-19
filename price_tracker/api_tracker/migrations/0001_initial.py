# Generated by Django 4.1.7 on 2025-01-07 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotifyCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case', models.CharField(max_length=8, unique=True)),
                ('text', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'verbose_name': 'notify_case',
                'verbose_name_plural': 'notify_cases',
                'ordering': ['case'],
            },
        ),
        migrations.CreateModel(
            name='NotifyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=32, unique=True)),
                ('text', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'verbose_name': 'notify_type',
                'verbose_name_plural': 'notify_types',
                'ordering': ['type'],
            },
        ),
        migrations.CreateModel(
            name='Tracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255, unique=True)),
                ('host', models.CharField(blank=True, max_length=255, null=True)),
                ('title', models.CharField(blank=True, max_length=128, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('date_time', models.DateTimeField(blank=True, null=True)),
                ('img_url', models.CharField(blank=True, max_length=254, null=True)),
                ('currency', models.CharField(blank=True, max_length=8, null=True)),
                ('in_stock', models.BooleanField(blank=True, null=True)),
                ('archive', models.BooleanField(blank=True, default=False, null=True)),
            ],
            options={
                'verbose_name': 'tracker',
                'verbose_name_plural': 'trackers',
            },
        ),
        migrations.CreateModel(
            name='UserTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify', models.BooleanField(blank=True, default=True, null=True)),
                ('need_notify_case', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('need_notify_types', models.ManyToManyField(blank=True, to='api_tracker.notifytype')),
                ('tracker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_tracker', to='api_tracker.tracker')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_tracker', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user_tracker',
                'verbose_name_plural': 'users_trackers',
            },
        ),
        migrations.CreateModel(
            name='TrackersUserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_task_ids', models.TextField(blank=True, default='', null=True)),
                ('notify_case', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api_tracker.notifycase')),
                ('notify_types', models.ManyToManyField(blank=True, to='api_tracker.notifytype')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trackers_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Trackers User Settings',
                'verbose_name_plural': 'Trackers Users Settings',
            },
        ),
        migrations.AddField(
            model_name='tracker',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='trackers', through='api_tracker.UserTracker', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('tracker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='api_tracker.tracker')),
            ],
        ),
    ]
