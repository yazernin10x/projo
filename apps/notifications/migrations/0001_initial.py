# Generated by Django 5.1.6 on 2025-03-10 00:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('content', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('recipients', models.ManyToManyField(related_name='received_notifications', to=settings.AUTH_USER_MODEL, verbose_name='Recipients')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_notifications', to=settings.AUTH_USER_MODEL, verbose_name='Sender')),
            ],
        ),
    ]
