
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion.scrapers.bbc_scraper import BBCScraper
from ingestion.kafka_producer.producer import NewsProducer
from ingestion.kafka_producer.schema import get_raw_news_schema_str

def test_pipeline():
    print("Initializing Pipeline Verification...")
    
    # 1. Initialize Producer
    try:
        producer = NewsProducer()
        print("✅ Kafka Producer connected successfully.")
    except Exception as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        return

    # 2. Run Scraper (Limit to 1 article for quick test)
    print("\nStarting Scraper (BBC)...")
    scraper = BBCScraper()
    headlines = scraper.scrape_headlines()
    
    if not headlines:
        print("⚠️ No headlines found. Exiting.")
        return

    print(f"Found {len(headlines)} headlines. Processing the first one...")
    
    article_url = headlines[0]['url']
    article_data = scraper.scrape_article(article_url)
    article_data['source'] = 'BBC' # Ensure source is set
    
    if not article_data:
        print("❌ Failed to scrape article details.")
        return
        
    print(f"✅ Scraped Article: {article_data.get('title')}")

    # 3. Modify Article to match Schema (add missing fields if any)
    # The schema check isn't strictly enforced by the producer class yet, but good practice
    
    # 4. Produce to Kafka
    print(f"\nSending to Kafka topic: {producer.topic}...")
    producer.produce_news(article_data)
    
    # Flush to ensure delivery
    producer.flush()
    print("✅ Message produced and flushed.")

if __name__ == "__main__":
    # Give Kafka a moment to settle if just started
    time.sleep(5)
    test_pipeline()
