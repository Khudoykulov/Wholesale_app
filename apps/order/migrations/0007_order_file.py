# Generated by Django 5.1.1 on 2025-02-08 16:53

import apps.order.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_order_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/', validators=[apps.order.models.validate_file_type]),
        ),
    ]
