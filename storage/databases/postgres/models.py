
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True, index=True)
    
    # Metadata
    url = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=func.now())
    
    # Content (Stored in Data Lake, but we keep short summary/text here if needed)
    # Ideally, heavy body text goes to MinIO (Parquet), but for simplicity we can store here too.
    body_text = Column(Text, nullable=True)
    
    # Processing Status
    is_processed = Column(Boolean, default=False)
    
    # NLP Enrichment
    sentiment_score = Column(Integer, nullable=True)     # e.g., 0-100 or raw score
    sentiment_label = Column(String, nullable=True)      # e.g., "POSITIVE", "NEGATIVE"
    embedding = Column(Text, nullable=True)              # Store vector as JSON string for now
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<NewsArticle(title={self.title}, source={self.source})>"
