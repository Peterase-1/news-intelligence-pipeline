
from typing import List, Dict
from ingestion.scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

class CNNScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://www.cnn.com/world", source_name="CNN")

    def scrape_headlines(self) -> List[Dict]:
        soup = self._get_page_content(self.base_url)
        if not soup:
            return []

        headlines = []
        # CNN links often start with /2024/ or /2025/ (date based)
        # and are usually within specific container classes.
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Filter for date-based article URLs
            if '/2024/' in href or '/2025/' in href or '/index.html' in href:
                 if href.startswith('/'):
                     full_url = f"https://www.cnn.com{href}"
                 elif href.startswith('https://www.cnn.com'):
                     full_url = href
                 else:
                     continue
                 
                 # unique check
                 if not any(d['url'] == full_url for d in headlines):
                    title = link.get_text().strip()
                    if title:
                        headlines.append({'url': full_url, 'title': title})

        return headlines[:5]

    def scrape_article(self, url: str) -> Dict:
        soup = self._get_page_content(url)
        if not soup:
            return {}

        data = {
            'url': url,
            'title': '',
            'body': '',
            'published_at': '',
            'author': 'CNN'
        }

        h1 = soup.find('h1')
        if h1:
            data['title'] = h1.get_text().strip()

        # CNN body text is usually in div class="article__content" or similar
        # paragraphs
        article_div = soup.find('div', class_='article__content')
        if not article_div:
            # Fallback for different templates
            article_div = soup.find('div', class_='story-body__content') # Old style?
        
        target_container = article_div if article_div else soup

        paragraphs = target_container.find_all('p')
        # Filter out "Read More" links or footer text often found in p tags
        clean_paragraphs = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20]
        data['body'] = " ".join(clean_paragraphs)
        
        # Date
        # usually in meta tag
        meta_date = soup.find('meta', property='article:published_time')
        if meta_date:
            data['published_at'] = meta_date['content']

        return data
