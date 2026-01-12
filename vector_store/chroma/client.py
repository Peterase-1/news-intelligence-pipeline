
import chromadb
from chromadb.config import Settings
import logging
import os

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsVectorStore:
    def __init__(self, persistence_path="chroma_db", collection_name="news_collection"):
        """
        Initializes the Vector Store.
        Stores data locally in 'persistence_path' folder.
        """
        self.path = os.path.abspath(os.path.join(os.getcwd(), persistence_path))
        logger.info(f"Initializing ChromaDB at: {self.path}")
        
        try:
            self.client = chromadb.PersistentClient(path=self.path)
            
            # Get or Create Collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"} # Use Cosine Similarity
            )
            logger.info(f"✅ Collection '{collection_name}' ready. Count: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"❌ Failed to init ChromaDB: {e}")
            raise e

    def add_articles(self, articles_data):
        """
        Adds articles to the vector store.
        
        Args:
            articles_data (list of dict): [
                {
                    "id": "url_or_unique_id",
                    "embedding": [0.1, 0.2, ...],
                    "metadata": {"title": "...", "source": "..."}
                    "document": "Full text content..."
                }
            ]
        """
        if not articles_data:
            return

        ids = [str(a["id"]) for a in articles_data]
        embeddings = [a["embedding"] for a in articles_data]
        documents = [a["document"] for a in articles_data]
        metadatas = [a["metadata"] for a in articles_data]

        try:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"✅ Upserted {len(articles_data)} articles to Vector Store.")
        except Exception as e:
            logger.error(f"❌ Failed to upsert: {e}")

    def search(self, query_embedding, n_results=5):
        """
        Searches for similar articles using a vector.
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return None

if __name__ == "__main__":
    # Test
    print("Testing Vector Store...")
    vs = NewsVectorStore(persistence_path="test_chroma_db")
    
    # Dummy Data
    vs.add_articles([{
        "id": "test_1",
        "embedding": [0.1] * 384, # Fake 384-dim vector
        "document": "This is a test article.",
        "metadata": {"source": "Test", "title": "Test Title"}
    }])
    
    print("Count:", vs.collection.count())
