# Generated by Django 4.2.5 on 2023-12-29 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_remove_admin_created_moderators_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_authenticated',
            field=models.BooleanField(default=True),
        ),
    ]
