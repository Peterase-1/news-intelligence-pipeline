
from typing import List, Dict
from ingestion.scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

class ReutersScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://www.reuters.com/world/", source_name="Reuters")

    def scrape_headlines(self) -> List[Dict]:
        soup = self._get_page_content(self.base_url)
        if not soup:
            return []

        headlines = []
        # Reuters format: /world/us/title-id/ or similar
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Basic filter
            if '/world/' in href and '-' in href:
                 if href.startswith('/'):
                     full_url = f"https://www.reuters.com{href}"
                 else:
                     full_url = href
                 
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
            'author': 'Reuters'
        }

        h1 = soup.find('h1')
        if h1:
            data['title'] = h1.get_text().strip()

        # Reuters article body
        article_body = soup.find('div', class_='article-body__content__17Yit')
        if not article_body:
             # Try searching by generalized attribute if class name is obfuscated
             article_body = soup.find('article')
        
        if article_body:
             paragraphs = article_body.find_all('p')
             data['body'] = " ".join([p.get_text().strip() for p in paragraphs])
        
        # Date
        time_tag = soup.find('time')
        if time_tag:
            data['published_at'] = time_tag.get('datetime', '')

        return data
