import requests
import os
from dotenv import load_dotenv
import feedparser
from datetime import datetime

# Load environment variables
load_dotenv()

class NewsAPI:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/"
    
    def get_ai_news(self, query="artificial intelligence", page_size=20):
        """Fetch AI news from NewsAPI"""
        url = f"{self.base_url}everything"
        params = {
            'q': query,
            'apiKey': self.api_key,
            'pageSize': page_size,
            'sortBy': 'publishedAt',
            'language': 'en'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from NewsAPI: {e}")
            return None

class RSSFetcher:
    def __init__(self):
        self.rss_feeds = [
            "https://news.google.com/rss/search?q=artificial+intelligence",
            "https://techcrunch.com/feed/",
            "https://feeds.arstechnica.com/arstechnica/index"
        ]
    
    def fetch_rss_news(self):
        """Fetch news from RSS feeds"""
        all_articles = []
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                print(f"Parsing {feed_url}: Found {len(feed.entries)} entries")
                
                for entry in feed.entries[:10]:  # Limit to 10 per feed
                    article = {
                        'title': entry.title,
                        'url': entry.link,
                        'published': entry.get('published', 'Unknown'),
                        'source': feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else 'RSS',
                        'description': entry.get('description', entry.get('summary', ''))
                    }
                    all_articles.append(article)
            except Exception as e:
                print(f"Error fetching RSS from {feed_url}: {e}")
        
        return all_articles

if __name__ == "__main__":
    # Test the APIs
    print("Testing NewsAPI...")
    news_api = NewsAPI()
    news_data = news_api.get_ai_news()
    
    if news_data and 'articles' in news_data:
        print(f"✅ NewsAPI working! Found {len(news_data['articles'])} articles")
        print(f"First article: {news_data['articles'][0]['title']}")
    else:
        print("❌ NewsAPI failed")
    
    print("\nTesting RSS feeds...")
    rss = RSSFetcher()
    rss_articles = rss.fetch_rss_news()
    print(f"✅ RSS working! Found {len(rss_articles)} articles")
