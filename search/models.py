# myapp/models.py
from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=255, default='')
    authors = models.TextField(max_length=255, default='[]')
    institutions = models.TextField(default='[]')
    keywords = models.TextField(default='')
    pdf_url = models.URLField(default='[]')
    bibliographie = models.TextField(default='[]')
    text = models.TextField(default='')
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
