
from typing import List, Dict
from ingestion.scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

class BBCScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://www.bbc.com/news", source_name="BBC")

    def scrape_headlines(self) -> List[Dict]:
        """
        Scrapes headline URLs from the main BBC News page.
        """
        soup = self._get_page_content(self.base_url)
        if not soup:
            return []

        headlines = []
        # BBC structure changes often, but we look for common article blocks
        # This is a heuristic and might need adjustment as the site evolves
        
        # Look for links that look like articles (contain /news/articles or /news/world)
        # Note: BBC URLs are often relative
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Basic filter for news articles
            if '/news/articles/' in href:
                full_url = href if href.startswith('http') else f"https://www.bbc.com{href}"
                
                # Check for duplicates
                if not any(d['url'] == full_url for d in headlines):
                    # Try to get title from text
                    title = link.get_text().strip()
                    if title:
                         headlines.append({'url': full_url, 'title': title})
        
        # Limit to first 5 for testing purposes to avoid spamming
        return headlines[:5]

    def scrape_article(self, url: str) -> Dict:
        """
        Extracts content from a generic BBC Article page.
        """
        soup = self._get_page_content(url)
        if not soup:
            return {}

        article_data = {
            'url': url,
            'title': '',
            'body': '',
            'published_at': '',
            'author': 'BBC News'
        }

        # Extract Title
        # Usually <h1>
        h1 = soup.find('h1')
        if h1:
            article_data['title'] = h1.get_text().strip()

        # Extract Body
        # BBC articles usually wrapped in <article> or specific div classes
        # A simple heuristic is to grab all <div data-component="text-block"> or similar
        # For now, let's grab all paragraphs in the main article container
        
        # Try to find the main article container
        article_tag = soup.find('article')
        if article_tag:
            paragraphs = article_tag.find_all('p')
            body_text = " ".join([p.get_text() for p in paragraphs])
            article_data['body'] = body_text
        else:
            # Fallback
            paragraphs = soup.find_all('p')
            body_text = " ".join([p.get_text() for p in paragraphs])
            article_data['body'] = body_text

        # Extract Date
        # Usually a <time> element
        time_tag = soup.find('time')
        if time_tag and time_tag.has_attr('datetime'):
             article_data['published_at'] = time_tag['datetime']

        return article_data
