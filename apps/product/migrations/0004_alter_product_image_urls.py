# Generated by Django 5.1.1 on 2024-09-29 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_image_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_urls',
            field=models.CharField(),
        ),
    ]
