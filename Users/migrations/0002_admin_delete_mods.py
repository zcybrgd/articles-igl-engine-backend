# Generated by Django 4.2.5 on 2024-01-03 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='delete_mods',
            field=models.IntegerField(default=0),
        ),
    ]
