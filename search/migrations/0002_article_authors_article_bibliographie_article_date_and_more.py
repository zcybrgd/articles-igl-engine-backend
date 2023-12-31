# Generated by Django 4.2.5 on 2023-12-22 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.JSONField(default='[]', max_length=255),
        ),
        migrations.AddField(
            model_name='article',
            name='bibliographie',
            field=models.TextField(default='[]'),
        ),
        migrations.AddField(
            model_name='article',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='institutions',
            field=models.TextField(default='[]'),
        ),
        migrations.AddField(
            model_name='article',
            name='keywords',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='article',
            name='pdf_url',
            field=models.URLField(default='[]'),
        ),
        migrations.AddField(
            model_name='article',
            name='text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(default='', max_length=255),
        ),
    ]