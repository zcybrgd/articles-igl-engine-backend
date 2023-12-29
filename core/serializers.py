from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):


    class Meta:
        model = Article
        fields = ['article_id', 'content', 'url_pdf']
        read_only_fields = ['article_id', 'content', 'url_pdf']



class ArticleUnReviewedSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    authors = serializers.ListField(child=serializers.CharField())
    institutions = serializers.ListField(child=serializers.CharField())
    keywords = serializers.CharField()
    pdf_url = serializers.URLField()
    bibliographie = serializers.ListField(child=serializers.CharField())
    abstract = serializers.CharField()
    text = serializers.CharField()
    date = serializers.CharField()