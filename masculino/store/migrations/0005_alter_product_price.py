# Generated by Django 4.0.6 on 2022-09-23 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_rename_side_image1_product_side_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.CharField(max_length=20),
        ),
    ]
