import os
from dotenv import load_dotenv
import feedparser
import requests
from datetime import datetime
from newsapi import NewsApiClient
from fuzzywuzzy import fuzz
import openai
import google.generativeai as genai
import hashlib
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import re

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
    
    def summarize_with_openai(self, title, description, content="", adhd_friendly=False):
        """Generate summary using OpenAI"""
        try:
            if not self.openai_api_key:
                return "OpenAI API key not configured"
            
            text_to_summarize = f"Title: {title}\nDescription: {description}\nContent: {content[:1000]}"
            
            if adhd_friendly:
                system_prompt = """You are an AI news analyst specializing in ADHD-friendly summaries. Create summaries that are:
- Bullet points instead of paragraphs
- Key insight first (most important info upfront)  
- Short, punchy sentences
- Action items if relevant
- Easy to scan quickly"""
                
                user_prompt = f"Create an ADHD-friendly summary of this AI news article:\n\n{text_to_summarize}\n\nFormat:\n• **Key Insight:** [main point]\n• **Why It Matters:** [implications]\n• **Bottom Line:** [actionable takeaway]"
            else:
                system_prompt = "You are an AI news analyst. Provide concise, informative summaries of AI-related articles. Focus on key insights, implications, and what makes this newsworthy."
                user_prompt = f"Summarize this AI news article in 2-3 sentences:\n\n{text_to_summarize}"
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200 if adhd_friendly else 150,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI summary error: {str(e)}"
    
    def summarize_with_gemini(self, title, description, content="", adhd_friendly=False):
        """Generate summary using Google Gemini"""
        try:
            if not self.google_api_key:
                return "Google API key not configured"
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            text_to_summarize = f"Title: {title}\nDescription: {description}\nContent: {content[:1000]}"
            
            if adhd_friendly:
                prompt = f"""Create an ADHD-friendly summary of this AI news article. Use this format:

• **Key Insight:** [main point in one sentence]
• **Why It Matters:** [implications and context]  
• **Bottom Line:** [actionable takeaway or what to expect]

Article to summarize:
{text_to_summarize}"""
            else:
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
class ArticleImageExtractor:
    @staticmethod
    def extract_image_from_url(url, timeout=5):
        """Extract the main image from an article URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different methods to find the main image
            image_url = None
            
            # Method 1: OpenGraph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image['content']
            
            # Method 2: Twitter card image
            if not image_url:
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image['content']
            
            # Method 3: First large image in article
            if not image_url:
                images = soup.find_all('img')
                for img in images:
                    src = img.get('src') or img.get('data-src')
                    if src and not any(skip in src.lower() for skip in ['logo', 'avatar', 'icon', 'ad']):
                        # Try to filter out small images
                        width = img.get('width')
                        height = img.get('height')
                        if width and height:
                            try:
                                if int(width) >= 300 and int(height) >= 200:
                                    image_url = src
                                    break
                            except (ValueError, TypeError):
                                continue
                        else:
                            # If no dimensions, take the first reasonable image
                            image_url = src
                            break
            
            # Ensure absolute URL
            if image_url:
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url.startswith('/'):
                    from urllib.parse import urljoin
                    image_url = urljoin(url, image_url)
            
            return image_url
            
        except Exception as e:
            print(f"Error extracting image from {url}: {e}")
            return None
    
    @staticmethod
    def get_placeholder_image(source=""):
        """Get a placeholder image based on source"""
        # Different placeholder images for different sources
        if "hacker news" in source.lower():
            return "https://picsum.photos/400/250?random=1&blur=1"
        elif "techcrunch" in source.lower():
            return "https://picsum.photos/400/250?random=2&blur=1"
        else:
            return "https://picsum.photos/400/250?random=3&blur=1"

class ArticleImageExtractor:
    @staticmethod
    def get_article_image(article_url, title=""):
        """Get image for article using multiple strategies"""
        
        # Strategy 1: Try to extract from article URL
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(article_url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for Open Graph image
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    return og_image.get('content')
                
                # Look for Twitter Card image
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    return twitter_image.get('content')
                
                # Look for first img tag in article
                img_tag = soup.find('img')
                if img_tag and img_tag.get('src'):
                    img_src = img_tag.get('src')
                    if img_src.startswith('http'):
                        return img_src
        except:
            pass
        
        # Strategy 2: Generate placeholder based on article content
        return ArticleImageExtractor.get_placeholder_image(title, article_url)
    
    @staticmethod
    def get_placeholder_image(title="", url=""):
        """Generate consistent placeholder images based on content"""
        
        # Create hash for consistency
        content_hash = hashlib.md5(f"{title}{url}".encode()).hexdigest()
        seed = int(content_hash[:8], 16)
        
        # AI/Tech themed images from Unsplash
        tech_topics = [
            "artificial-intelligence",
            "machine-learning", 
            "robot",
            "computer-code",
            "data-science",
            "neural-network",
            "technology",
            "programming",
            "algorithm",
            "digital"
        ]
        
        # Pick topic based on hash
        topic = tech_topics[seed % len(tech_topics)]
        
        # Use Unsplash for high-quality images
        image_id = 400 + (seed % 100)  # Random image IDs
        return f"https://picsum.photos/id/{image_id}/400/250"
    
    @staticmethod 
    def get_source_specific_image(source, title=""):
        """Get source-specific placeholder images"""
        
        content_hash = hashlib.md5(f"{title}".encode()).hexdigest()
        seed = int(content_hash[:8], 16)
        image_id = 100 + (seed % 300)
        
        if source == "Hacker News":
            # Orange-themed for HN
            return f"https://picsum.photos/id/{image_id}/400/250?grayscale&blur=1"
        elif "TechCrunch" in source:
            # Green-themed for TechCrunch
            return f"https://picsum.photos/id/{image_id}/400/250"
        else:
            # Default tech image
            return f"https://picsum.photos/id/{image_id}/400/250"

