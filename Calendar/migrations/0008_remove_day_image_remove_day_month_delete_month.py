# Generated by Django 4.2.1 on 2023-06-10 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Calendar', '0007_day_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='day',
            name='image',
        ),
        migrations.RemoveField(
            model_name='day',
            name='month',
        ),
        migrations.DeleteModel(
            name='Month',
        ),
    ]