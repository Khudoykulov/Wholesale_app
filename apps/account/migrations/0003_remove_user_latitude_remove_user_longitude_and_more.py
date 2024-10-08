# Generated by Django 5.1.1 on 2024-09-29 12:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_user_latitude_user_longitude'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='user',
            name='longitude',
        ),
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.CharField(max_length=100)),
                ('longitude', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='location', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
