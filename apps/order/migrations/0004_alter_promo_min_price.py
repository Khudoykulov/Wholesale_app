# Generated by Django 5.1.1 on 2024-11-14 18:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_remove_order_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promo',
            name='min_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(100.0)]),
        ),
    ]
