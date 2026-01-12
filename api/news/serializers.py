
from rest_framework import serializers
from .models import NewsArticle

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'url', 'title', 'source', 'published_at', 
            'sentiment_label', 'sentiment_score', 'created_at'
        ]
        # We exclude 'embedding' and 'body_text' from list view to save bandwidth
        # but maybe we want body_text in detailed view?
        # For now, let's include basic info.
