# Generated by Django 5.1.1 on 2024-11-13 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_cartitem_is_ordered_order_is_delivered_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='amount',
        ),
    ]
