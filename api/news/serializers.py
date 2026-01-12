
from rest_framework import serializers
from .models import NewsArticle

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'url', 'title', 'source', 'published_at', 
            'sentiment_label', 'sentiment_score', 'created_at'
        ]
