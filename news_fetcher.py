import os
from dotenv import load_dotenv
import feedparser
import requests
from datetime import datetime
from newsapi import NewsApiClient
from fuzzywuzzy import fuzz
import openai
import google.generativeai as genai

# Load environment variables
load_dotenv()

class NewsAPI:
    def __init__(self):
        api_key = os.getenv('NEWS_API_KEY')
        self.newsapi = NewsApiClient(api_key=api_key)
    
    def get_ai_news(self, query="artificial intelligence", page_size=20):
        """Fetch AI news from NewsAPI using official client"""
        try:
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=page_size
            )
            return response
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return None

    def get_top_ai_headlines(self, page_size=20):
        """Get top AI headlines"""
        try:
            response = self.newsapi.get_top_headlines(
                q='artificial intelligence',
                language='en',
                page_size=page_size
            )
            return response
        except Exception as e:
            print(f"Error fetching top headlines: {e}")
            return None

class HackerNewsFetcher:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    def get_ai_stories(self, limit=20):
        """Fetch AI-related stories from Hacker News"""
        try:
            # Get top stories
            top_stories_url = f"{self.base_url}/topstories.json"
            response = requests.get(top_stories_url, timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:100]  # Get top 100 to filter
            
            ai_stories = []
            ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 
                          'neural', 'llm', 'gpt', 'openai', 'deepmind', 'chatgpt']
            
            for story_id in story_ids[:limit*2]:  # Get extra to account for filtering
                story_url = f"{self.base_url}/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=5)
                if story_response.status_code == 200:
                    story = story_response.json()
                    
                    if story and story.get('title'):
                        title_lower = story['title'].lower()
                        if any(keyword in title_lower for keyword in ai_keywords):
                            ai_stories.append({
                                'title': story['title'],
                                'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                'source': 'Hacker News',
                                'published': datetime.fromtimestamp(story.get('time', 0)).isoformat() if story.get('time') else 'Unknown',
                                'description': story.get('text', '')[:200] + '...' if story.get('text') else '',
                                'score': story.get('score', 0)
                            })
                
                if len(ai_stories) >= limit:
                    break
            
            return ai_stories
        except Exception as e:
            print(f"Error fetching from Hacker News: {e}")
            return []

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
                
                for entry in feed.entries[:10]:
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

class ArticleDeduplicator:
    @staticmethod
    def remove_duplicates(articles, similarity_threshold=80):
        """Remove duplicate articles based on title similarity"""
        if not articles:
            return articles
        
        unique_articles = []
        processed_titles = []
        
        for article in articles:
            title = article.get('title', '')
            is_duplicate = False
            
            for processed_title in processed_titles:
                similarity = fuzz.ratio(title.lower(), processed_title.lower())
                if similarity > similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                processed_titles.append(title)
        
        print(f"Removed {len(articles) - len(unique_articles)} duplicates")
        return unique_articles

class AISummaryGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
    
    def summarize_with_openai(self, title, description, content=""):
        """Generate summary using OpenAI"""
        try:
            if not self.openai_api_key:
                return "OpenAI API key not configured"
            
            text_to_summarize = f"Title: {title}\nDescription: {description}\nContent: {content[:1000]}"
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI news analyst. Provide concise, informative summaries of AI-related articles. Focus on key insights, implications, and what makes this newsworthy."},
                    {"role": "user", "content": f"Summarize this AI news article in 2-3 sentences:\n\n{text_to_summarize}"}
                ],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI summary error: {str(e)}"
    
    def summarize_with_gemini(self, title, description, content=""):
        """Generate summary using Google Gemini"""
        try:
            if not self.google_api_key:
                return "Google API key not configured"
            
            model = genai.GenerativeModel('gemini-pro')
            text_to_summarize = f"Title: {title}\nDescription: {description}\nContent: {content[:1000]}"
            
            prompt = f"Summarize this AI news article in 2-3 sentences, focusing on key insights and implications:\n\n{text_to_summarize}"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini summary error: {str(e)}"

if __name__ == "__main__":
    print("Testing all news sources...")
    
    # Test NewsAPI
    print("\n=== NewsAPI ===")
    news_api = NewsAPI()
    news_data = news_api.get_ai_news(page_size=5)
    if news_data and news_data['status'] == 'ok':
        print(f"✅ Found {len(news_data['articles'])} NewsAPI articles")
    
    # Test Hacker News
    print("\n=== Hacker News ===")
    hn = HackerNewsFetcher()
    hn_stories = hn.get_ai_stories(limit=5)
    print(f"✅ Found {len(hn_stories)} Hacker News stories")
    if hn_stories:
        print(f"Top HN story: {hn_stories[0]['title']}")
    
    # Test deduplication
    print("\n=== Testing Deduplication ===")
    all_articles = []
    if news_data and news_data['status'] == 'ok':
        for article in news_data['articles'][:3]:
            all_articles.append({
                'title': article['title'],
                'source': article['source']['name']
            })
    
    all_articles.extend([{'title': story['title'], 'source': story['source']} for story in hn_stories[:3]])
    
    print(f"Before dedup: {len(all_articles)} articles")
    unique_articles = ArticleDeduplicator.remove_duplicates(all_articles)
    print(f"After dedup: {len(unique_articles)} articles")
