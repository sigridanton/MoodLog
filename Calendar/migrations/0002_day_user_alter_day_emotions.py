# Generated by Django 4.2.1 on 2023-06-03 23:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Calendar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='day',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='day',
            name='emotions',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('1', 'Happy'), ('2', 'Excited'), ('3', 'Proud'), ('4', 'Relaxed'), ('5', 'Laughative'), ('6', 'Neutral'), ('7', 'Sad'), ('8', 'Angry'), ('9', 'Annoyed'), ('10', 'Depressed'), ('11', 'Stressed'), ('12', 'Tired'), ('13', 'Anxious'), ('14', 'Lonely')], max_length=2),
        ),
    ]