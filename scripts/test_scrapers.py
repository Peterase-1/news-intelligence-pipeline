
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion.scrapers.bbc_scraper import BBCScraper
from ingestion.scrapers.cnn_scraper import CNNScraper
from ingestion.scrapers.aljazeera_scraper import AlJazeeraScraper
from ingestion.scrapers.reuters_scraper import ReutersScraper

def main():
    print("Testing News Scrapers...")
    
    # Test BBC
    print("\n--- Running BBC Scraper ---")
    bbc = BBCScraper()
    bbc_articles = bbc.run()
    for art in bbc_articles:
        print(f"[BBC] Title: {art['title']}")
        print(f"      URL: {art['url']}")
        print(f"      Date: {art.get('published_at', 'N/A')}")
        print(f"      Body Length: {len(art['body'])} chars")
        print("-" * 50)

    # Test CNN
    print("\n--- Running CNN Scraper ---")
    cnn = CNNScraper()
    cnn_articles = cnn.run()
    for art in cnn_articles:
        print(f"[CNN] Title: {art['title']}")
        print(f"      URL: {art['url']}")
        print(f"      Date: {art.get('published_at', 'N/A')}")
        print(f"      Body Length: {len(art['body'])} chars")
        print("-" * 50)

    # Test Al Jazeera
    print("\n--- Running Al Jazeera Scraper ---")
    aj = AlJazeeraScraper()
    aj_articles = aj.run()
    for art in aj_articles:
        print(f"[Al Jazeera] Title: {art['title']}")
        print(f"      URL: {art['url']}")
        print(f"      Date: {art.get('published_at', 'N/A')}")
        print(f"      Body Length: {len(art['body'])} chars")
        print("-" * 50)

    # Test Reuters
    print("\n--- Running Reuters Scraper ---")
    reuters = ReutersScraper()
    reuters_articles = reuters.run()
    for art in reuters_articles:
        print(f"[Reuters] Title: {art['title']}")
        print(f"      URL: {art['url']}")
        print(f"      Date: {art.get('published_at', 'N/A')}")
        print(f"      Body Length: {len(art['body'])} chars")
        print("-" * 50)

if __name__ == "__main__":
    main()
