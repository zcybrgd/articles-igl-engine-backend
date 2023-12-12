from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):


    class Meta:
        model = Article
        fields = ['article_id', 'content', 'url_pdf']
        read_only_fields = ['article_id', 'content', 'url_pdf']
