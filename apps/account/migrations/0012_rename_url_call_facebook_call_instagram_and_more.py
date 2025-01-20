# Generated by Django 5.1.1 on 2025-01-20 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_call'),
    ]

    operations = [
        migrations.RenameField(
            model_name='call',
            old_name='url',
            new_name='facebook',
        ),
        migrations.AddField(
            model_name='call',
            name='instagram',
            field=models.CharField(blank=True, max_length=123, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='telegram',
            field=models.CharField(blank=True, max_length=123, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='tiktok',
            field=models.CharField(blank=True, max_length=123, null=True),
        ),
    ]
