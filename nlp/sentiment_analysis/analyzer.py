
from transformers import pipeline
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, model_name="distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initializes the Sentiment Analyzer with a pre-trained model.
        Default: DistilBERT (Fast & Accurate)
        """
        logger.info(f"Loading Sentiment Model: {model_name}...")
        try:
            self.analyzer = pipeline("sentiment-analysis", model=model_name)
            logger.info("✅ Sentiment Model loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise e

    def analyze(self, text):
        """
        Analyzes the sentiment of a text string.
        Returns: 
            dict: {'label': 'POSITIVE'|'NEGATIVE', 'score': float}
        """
        if not text or len(text.strip()) == 0:
            return None

        # Truncate text to 512 tokens approx (DistilBERT limit) to avoid crashing
        # A rough char limit is 2000 chars.
        truncated_text = text[:2000]
        
        try:
            result = self.analyzer(truncated_text)[0]
            # Result format: {'label': 'POSITIVE', 'score': 0.99}
            return result
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return None

if __name__ == "__main__":
    # Quick Test
    print("Testing Analyzer...")
    sa = SentimentAnalyzer()
    examples = [
        "The stock market crashed today, causing panic.",
        "Scientists discovered a cure for cancer! This is amazing.",
        "The weather is okay, I guess."
    ]
    
    for ex in examples:
        print(f"Text: {ex}")
        print(f"Result: {sa.analyze(ex)}")
