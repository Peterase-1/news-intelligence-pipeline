
import logging
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract Base Class for News Scrapers.
    Handles common logic like request headers, retries, and logging.
    """

    def __init__(self, base_url: str, source_name: str):
        self.base_url = base_url
        self.source_name = source_name
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetches the page content and returns a BeautifulSoup object.
        Includes simple retry logic and random delays to be polite.
        """
        try:
            # Polite delay
            time.sleep(random.uniform(1.0, 3.0))
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    @abstractmethod
    def scrape_headlines(self) -> List[Dict]:
        """
        Scrapes the main page to find article URLs and metadata.
        Returns a list of dictionaries with basic info (url, title).
        """
        pass

    @abstractmethod
    def scrape_article(self, url: str) -> Dict:
        """
        Scrapes the full content of a specific article.
        Returns a complete dictionary with title, body, author, date, etc.
        """
        pass

    def run(self) -> List[Dict]:
        """
        Main execution method. Scrapes headlines and then the details for each.
        """
        logger.info(f"Starting scrape for {self.source_name}...")
        articles = []
        headlines = self.scrape_headlines()
        
        logger.info(f"Found {len(headlines)} headlines. Starting detailed scrape...")

        for item in headlines:
            article_url = item.get('url')
            if article_url:
                try:
                    logger.info(f"Scraping article: {article_url}")
                    details = self.scrape_article(article_url)
                    if details:
                        # Merge headline info if needed, or just use details
                        # Ensure source_name is present
                        details['source'] = self.source_name
                        details['scraped_at'] = datetime.now().isoformat()
                        articles.append(details)
                except Exception as e:
                    logger.error(f"Failed to scrape article {article_url}: {e}")
        
        logger.info(f"Completed scrape for {self.source_name}. Total articles: {len(articles)}")
        return articles
