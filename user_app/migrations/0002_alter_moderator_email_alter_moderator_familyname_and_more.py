# Generated by Django 4.2.5 on 2023-12-14 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderator',
            name='email',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='moderator',
            name='familyName',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='moderator',
            name='firstName',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='moderator',
            name='imgUrl',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='moderator',
            name='password',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='moderator',
            name='userName',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(max_length=110),
        ),
        migrations.AlterField(
            model_name='user',
            name='userName',
            field=models.CharField(max_length=110),
        ),
    ]
