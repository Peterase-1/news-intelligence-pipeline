
from sentence_transformers import SentenceTransformer
import logging
import numpy as np

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initializes the Embedding Generator.
        Default: all-MiniLM-L6-v2 (384 dimensions, very fast)
        """
        logger.info(f"Loading Embedding Model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("✅ Embedding Model loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise e

    def generate(self, text):
        """
        Generates a vector embedding for the given text.
        Returns: 
            list[float]: The vector (e.g., [0.1, -0.5, 0.03, ...])
        """
        if not text or len(text.strip()) == 0:
            return None

        try:
            # Generate embedding
            # normalize_embeddings=True makes cosine similarity easier later
            vector = self.model.encode(text, normalize_embeddings=True)
            
            # Convert numpy array to standard list (for JSON serialization)
            return vector.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

if __name__ == "__main__":
    print("Testing Embedding Generator...")
    eg = EmbeddingGenerator()
    
    text = "The news intelligence pipeline is built with Spark and Kafka."
    vector = eg.generate(text)
    
    print(f"Text: {text}")
    print(f"Vector Dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
