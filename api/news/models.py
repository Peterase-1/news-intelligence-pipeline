
from django.db import models

class NewsArticle(models.Model):
    # Map to existing columns
    url = models.CharField(max_length=2048, unique=True)
    source = models.CharField(max_length=255)
    title = models.CharField(max_length=1024)
    author = models.CharField(max_length=255, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    # Content
    body_text = models.TextField(null=True, blank=True)
    
    # Status
    is_processed = models.BooleanField(default=False)
    
    # NLP Enrichment
    sentiment_score = models.IntegerField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=50, null=True, blank=True)
    embedding = models.TextField(null=True, blank=True) # Stored as JSON string
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # Django will NOT create/modify this table
        db_table = 'news_articles'
        ordering = ['-published_at']

    def __str__(self):
        return self.title
