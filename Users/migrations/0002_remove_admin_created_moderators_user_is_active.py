# Generated by Django 4.2.5 on 2023-12-29 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='created_moderators',
        ),
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='active'),
        ),
    ]