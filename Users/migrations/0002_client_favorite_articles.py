# Generated by Django 4.2.5 on 2023-12-27 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='favorite_articles',
            field=models.CharField(blank=True, max_length=110),
        ),
    ]
