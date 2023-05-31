# Generated by Django 4.0.6 on 2022-09-23 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='images',
        ),
        migrations.AddField(
            model_name='product',
            name='main_image',
            field=models.ImageField(default=None, upload_to=''),
        ),
        migrations.AddField(
            model_name='product',
            name='side_image1',
            field=models.ImageField(default=None, upload_to=''),
        ),
        migrations.AddField(
            model_name='product',
            name='side_image2',
            field=models.ImageField(default=None, upload_to=''),
        ),
    ]