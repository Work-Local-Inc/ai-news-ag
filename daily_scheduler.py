import schedule
import time
import os
from datetime import datetime
from news_fetcher import NewsAPI, HackerNewsFetcher, ArticleDeduplicator
from slack_notifier import SlackNotifier

class DailyNewsScheduler:
    """Handles scheduled daily news scraping and Slack notifications"""
    
    def __init__(self):
        self.news_api = NewsAPI()
        self.hn_fetcher = HackerNewsFetcher()
        self.deduplicator = ArticleDeduplicator()
        self.slack = SlackNotifier()
    
    def fetch_daily_news(self) -> tuple:
        """Fetch and deduplicate daily news"""
        print(f"🔄 Starting daily news fetch at {datetime.now()}")
        
        all_articles = []
        stats = {'hacker_news_count': 0, 'news_api_count': 0}
        
        # Fetch Hacker News
        try:
            print("📰 Fetching Hacker News...")
            hn_articles = self.hn_fetcher.get_top_stories(limit=10)
            if hn_articles:
                all_articles.extend(hn_articles)
                stats['hacker_news_count'] = len(hn_articles)
                print(f"✅ Got {len(hn_articles)} Hacker News articles")
        except Exception as e:
            print(f"❌ Error fetching Hacker News: {e}")
        
        # Fetch from NewsAPI
        try:
            print("🌐 Fetching NewsAPI...")
            news_response = self.news_api.get_ai_news(query="artificial intelligence", page_size=15)
            if news_response and news_response.get('status') == 'ok':
                news_articles = []
                for article in news_response['articles']:
                    news_articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['url'],
                        'published': article['publishedAt'],
                        'source': article['source']['name'],
                        'content': article.get('content', ''),
                        'image_url': article.get('urlToImage')
                    })
                all_articles.extend(news_articles)
                stats['news_api_count'] = len(news_articles)
                print(f"✅ Got {len(news_articles)} NewsAPI articles")
        except Exception as e:
            print(f"❌ Error fetching NewsAPI: {e}")
        
        # Deduplicate articles
        if all_articles:
            print("🔍 Deduplicating articles...")
            deduplicated = self.deduplicator.deduplicate_articles(all_articles)
            print(f"📊 Deduplicated {len(all_articles)} -> {len(deduplicated)} articles")
            return deduplicated, stats
        
        return [], stats
    
    def send_daily_update(self):
        """Main function to fetch news and send to Slack"""
        try:
            articles, stats = self.fetch_daily_news()
            
            if not articles:
                print("⚠️ No articles found for daily update")
                return
            
            print(f"📤 Sending {len(articles)} articles to Slack...")
            success = self.slack.send_daily_news(articles, stats)
            
            if success:
                print("✅ Daily news update sent successfully!")
            else:
                print("❌ Failed to send daily news update")
                
        except Exception as e:
            print(f"❌ Error in daily update: {e}")
    
    def test_slack_connection(self):
        """Test Slack integration"""
        print("🧪 Testing Slack connection...")
        if self.slack.test_connection():
            print("✅ Slack connection test successful!")
        else:
            print("❌ Slack connection test failed!")
    
    def run_scheduler(self):
        """Run the scheduler - call this to start the daily scheduling"""
        print("🚀 Starting AI News Daily Scheduler...")
        print("📅 Scheduled to run at 8:00 AM daily")
        
        # Schedule the daily job
        schedule.every().day.at("08:00").do(self.send_daily_update)
        
        # Optional: Add a test job every minute (remove in production)
        # schedule.every().minute.do(self.send_daily_update)
        
        print("⏰ Scheduler is running... Press Ctrl+C to stop")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Entry point for the scheduler"""
    scheduler = DailyNewsScheduler()
    
    # Test Slack connection first
    scheduler.test_slack_connection()
    
    # Uncomment to test sending immediately:
    # scheduler.send_daily_update()
    
    # Start the scheduler
    scheduler.run_scheduler()

if __name__ == "__main__":
    main() 