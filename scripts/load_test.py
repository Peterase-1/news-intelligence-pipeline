
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion.scrapers.bbc_scraper import BBCScraper
from ingestion.scrapers.cnn_scraper import CNNScraper
from ingestion.scrapers.aljazeera_scraper import AlJazeeraScraper
from ingestion.kafka_producer.producer import NewsProducer

def run_load_test():
    print("🚀 Starting Volume Load Test (30 Articles)...")
    
    producer = NewsProducer()
    total_produced = 0
    
    scrapers = [
        (BBCScraper(), "BBC"),
        (CNNScraper(), "CNN"),
        (AlJazeeraScraper(), "Al Jazeera")
    ]
    
    for scraper, name in scrapers:
        print(f"\n📡 Running Scraper: {name}")
        try:
            articles = scraper.run()
            count = 0
            
            # Send up to 10 articles per source
            for article in articles[:10]:
                print(f"   -> Sending: {article['title'][:50]}...")
                producer.produce_news(article)
                count += 1
                total_produced += 1
                time.sleep(0.5) # Simulate slight throttling
            
            print(f"   ✅ Sent {count} articles from {name}")
            
        except Exception as e:
            print(f"   ❌ Scraper {name} failed: {e}")
            
    producer.flush()
    print(f"\n✨ Load Test Complete. Total Articles Sent: {total_produced}")

if __name__ == "__main__":
    run_load_test()
