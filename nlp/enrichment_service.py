
import sys
import os
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.databases.postgres.models import NewsArticle
from storage.databases.postgres.db_manager import DATABASE_URL
from nlp.sentiment_analysis.analyzer import SentimentAnalyzer
from nlp.embeddings.generator import EmbeddingGenerator

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_enrichment():
    logger.info("🧠 Starting NLP Enrichment Service...")
    
    # 1. Initialize Models
    try:
        sentiment_analyzer = SentimentAnalyzer()
        embedding_generator = EmbeddingGenerator()
    except Exception as e:
        logger.error(f"Failed to initialize models: {e}")
        return

    # 2. Connect to DB
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 3. Fetch Articles that need processing
        # Criteria: sentiment_label is NULL (meaning we haven't touched it yet)
        articles = session.query(NewsArticle).filter(NewsArticle.sentiment_label == None).all()
        
        logger.info(f"🔍 Found {len(articles)} articles to enrich.")
        
        for article in articles:
            logger.info(f"   -> Processing: {article.title[:50]}...")
            
            # A. Sentiment
            text_for_sentiment = f"{article.title}. {article.body_text or ''}"
            sentiment = sentiment_analyzer.analyze(text_for_sentiment)
            
            if sentiment:
                article.sentiment_label = sentiment['label']
                # Convert 0.999 to integer score (0-100)
                # If NEGATIVE, make it negative? Or just store raw score?
                # Let's map: Positive(0.9) -> 90. Negative(0.9) -> -90.
                score = int(sentiment['score'] * 100)
                if sentiment['label'] == 'NEGATIVE':
                    score = -score
                article.sentiment_score = score
            
            # B. Embeddings
            # Combine title + source + body for semantic Search
            text_for_embedding = f"Title: {article.title} Source: {article.source} Content: {article.body_text or ''}"
            vector = embedding_generator.generate(text_for_embedding)
            
            if vector:
                article.embedding = json.dumps(vector) # Store as JSON string

            # Commit periodically or at end?
            # Doing per article for safety in this demo
            session.commit()
            
        logger.info("✨ Enrichment Complete.")
        
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    run_enrichment()
