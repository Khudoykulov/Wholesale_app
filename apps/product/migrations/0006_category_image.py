# Generated by Django 5.1.1 on 2024-10-04 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_remove_commentimage_comment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(default=1, upload_to='categories'),
            preserve_default=False,
        ),
    ]
