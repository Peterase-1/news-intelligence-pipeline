
from typing import List, Dict
from ingestion.scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

class AlJazeeraScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://www.aljazeera.com/news/", source_name="AlJazeera")

    def scrape_headlines(self) -> List[Dict]:
        soup = self._get_page_content(self.base_url)
        if not soup:
            return []

        headlines = []
        # Al Jazeera uses typical article tags
        # Look for links containing /year/month/day/title format or simplified structure
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # They usually start with /news/ or date based e.g. /2024/
            if '/news/' in href or '/2024/' in href:
                 if href.startswith('/'):
                     full_url = f"https://www.aljazeera.com{href}"
                 elif href.startswith('https://www.aljazeera.com'):
                     full_url = href
                 else:
                     continue
                 
                 # Basic de-duplication and noise filtering
                 if not any(d['url'] == full_url for d in headlines) and len(href) > 20:
                    # Try to extract title
                    title = link.get_text().strip()
                    if not title:
                        # Sometimes title is nested in a span or has visually-hidden class
                        nested_span = link.find('span')
                        if nested_span:
                            title = nested_span.get_text().strip()
                    
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
            'author': 'Al Jazeera Staff'
        }

        h1 = soup.find('h1')
        if h1:
            data['title'] = h1.get_text().strip()

        # Body text usually in main content area
        # Look for 'wysiwyg' class or specific article-body id
        main_content = soup.find('div', class_='wysiwyg')
        if not main_content:
             main_content = soup.find('main')
        
        if main_content:
            paragraphs = main_content.find_all('p')
            data['body'] = " ".join([p.get_text().strip() for p in paragraphs])
        
        # Date
        # Usually in meta or specific header info
        date_span = soup.find('span', class_='screen-reader-text') # Sometimes they hide it
        if not date_span:
             # Try generic meta
             meta_date = soup.find('meta', property='article:published_time')
             if meta_date:
                 data['published_at'] = meta_date['content']

        return data
