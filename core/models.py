from django.db import models


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    content = models.TextField()
    url_pdf = models.TextField()
    def __str__(self):
        return self.url_pdf

    class Meta:
        indexes = [
            models.Index(fields=['article_id'], name='article_pkey'),
        ]
