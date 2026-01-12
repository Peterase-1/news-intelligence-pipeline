
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
from vector_store.chroma.client import NewsVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_data():
    logger.info("🔄 Syncing Postgres -> ChromaDB...")
    
    # 1. Init Vector Store
    vs = NewsVectorStore()
    
    # 2. Connect to DB
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 3. Fetch Enriched Articles
        articles = session.query(NewsArticle).filter(NewsArticle.embedding != None).all()
        logger.info(f"🔍 Found {len(articles)} enriched articles in DB.")
        
        batch_data = []
        for art in articles:
            try:
                # Prepare data for Vector Store
                embedding_list = json.loads(art.embedding)
                
                # Check dim check
                # if len(embedding_list) != 384: skip...
                
                batch_data.append({
                    "id": str(art.url), # unique ID
                    "embedding": embedding_list,
                    "document": f"{art.title}. {art.body_text or ''}"[:5000], # Store content for retrieval (limit size)
                    "metadata": {
                        "title": art.title,
                        "source": art.source,
                        "published_at": str(art.published_at),
                        "sentiment": art.sentiment_label or "UNKNOWN"
                    }
                })
            except Exception as e:
                logger.error(f"Error parsing article {art.id}: {e}")

        # 4. Upsert
        if batch_data:
            vs.add_articles(batch_data)
        else:
            logger.warning("No data to sync.")

        logger.info("✨ Sync Complete.")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    sync_data()
