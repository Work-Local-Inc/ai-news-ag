#!/usr/bin/env python3
"""
Streamlit Cloud Scheduler - Runs daily news updates using Streamlit secrets
Perfect for Streamlit Cloud deployment
"""

import streamlit as st
import schedule
import time
import threading
from datetime import datetime
from news_fetcher import NewsAPI, HackerNewsFetcher, ArticleDeduplicator
from slack_notifier import SlackNotifier
import os

class StreamlitScheduler:
    """Scheduler that works with Streamlit Cloud and uses st.secrets"""
    
    def __init__(self):
        # Use Streamlit secrets if available, fallback to environment
        try:
            self.news_api_key = st.secrets.get("NEWS_API_KEY", os.getenv("NEWS_API_KEY"))
            self.slack_bot_token = st.secrets.get("SLACK_BOT_TOKEN", os.getenv("SLACK_BOT_TOKEN"))
            self.slack_channel = st.secrets.get("SLACK_CHANNEL", os.getenv("SLACK_CHANNEL", "#ai-news"))
        except:
            # Fallback to environment variables
            self.news_api_key = os.getenv("NEWS_API_KEY")
            self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
            self.slack_channel = os.getenv("SLACK_CHANNEL", "#ai-news")
        
        # Temporarily set environment variables for the fetchers
        if self.news_api_key:
            os.environ["NEWS_API_KEY"] = self.news_api_key
        if self.slack_bot_token:
            os.environ["SLACK_BOT_TOKEN"] = self.slack_bot_token
        if self.slack_channel:
            os.environ["SLACK_CHANNEL"] = self.slack_channel
        
        # Initialize components
        self.news_api = NewsAPI()
        self.hn_fetcher = HackerNewsFetcher()
        self.deduplicator = ArticleDeduplicator()
        self.slack = SlackNotifier()
        
        self.is_running = False
        self.scheduler_thread = None
    
    def fetch_and_send_news(self):
        """Fetch news and send to Slack"""
        try:
            st.write(f"🔄 Starting news fetch at {datetime.now()}")
            
            all_articles = []
            stats = {'hacker_news_count': 0, 'news_api_count': 0}
            
            # Fetch Hacker News
            try:
                st.write("📰 Fetching from Hacker News...")
                hn_articles = self.hn_fetcher.get_ai_stories(limit=10)
                if hn_articles:
                    all_articles.extend(hn_articles)
                    stats['hacker_news_count'] = len(hn_articles)
                    st.write(f"   ✅ Got {len(hn_articles)} Hacker News articles")
            except Exception as e:
                st.write(f"   ❌ Hacker News error: {e}")
            
            # Fetch NewsAPI
            try:
                st.write("🌐 Fetching from NewsAPI...")
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
                    st.write(f"   ✅ Got {len(news_articles)} NewsAPI articles")
            except Exception as e:
                st.write(f"   ❌ NewsAPI error: {e}")
            
            # Deduplicate
            if all_articles:
                st.write("🔍 Deduplicating articles...")
                deduplicated = self.deduplicator.remove_duplicates(all_articles, 80)
                st.write(f"   📊 {len(all_articles)} -> {len(deduplicated)} articles")
                
                # Send to Slack
                st.write(f"📤 Sending {len(deduplicated[:8])} articles to Slack...")
                if self.slack.send_daily_news(deduplicated[:8], stats):
                    st.success("✅ Daily news sent to Slack successfully!")
                    return True
                else:
                    st.error("❌ Failed to send to Slack")
                    return False
            else:
                st.warning("⚠️ No articles found")
                return False
                
        except Exception as e:
            st.error(f"❌ Error in news fetch: {e}")
            return False
    
    def schedule_job(self):
        """Background scheduler function"""
        schedule.every().day.at("08:00").do(self.fetch_and_send_news)
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self.schedule_job, daemon=True)
            self.scheduler_thread.start()
            return True
        return False
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
        return True

def create_scheduler_ui():
    """Create Streamlit UI for the scheduler"""
    st.markdown("---")
    st.markdown("## ⏰ Automated Daily Scheduler")
    
    # Initialize scheduler in session state
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = StreamlitScheduler()
    
    scheduler = st.session_state.scheduler
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🕗 Automated Daily Updates**
        - Runs at 8:00 AM daily
        - Fetches latest AI news
        - Sends to Slack automatically
        - Uses Streamlit secrets
        """)
        
        if st.button("🚀 Start Daily Scheduler", use_container_width=True):
            if scheduler.start_scheduler():
                st.success("✅ Daily scheduler started! Will run at 8 AM daily.")
                st.session_state.scheduler_running = True
            else:
                st.warning("⚠️ Scheduler already running")
        
        if st.button("⏹️ Stop Scheduler", use_container_width=True):
            if scheduler.stop_scheduler():
                st.success("✅ Scheduler stopped")
                st.session_state.scheduler_running = False
            else:
                st.warning("⚠️ Scheduler was not running")
    
    with col2:
        st.markdown("**🧪 Manual Controls**")
        
        if st.button("📤 Send News Now", use_container_width=True):
            with st.spinner("Fetching and sending news..."):
                if scheduler.fetch_and_send_news():
                    st.balloons()
                
        if st.button("🔧 Test Configuration", use_container_width=True):
            st.write("📋 Configuration Check:")
            st.write(f"   NewsAPI: {'✅' if scheduler.news_api_key else '❌'}")
            st.write(f"   Slack Bot: {'✅' if scheduler.slack_bot_token else '❌'}")
            st.write(f"   Channel: {scheduler.slack_channel}")
            
            if scheduler.slack_bot_token:
                if scheduler.slack.test_connection():
                    st.success("✅ Slack connection works!")
                else:
                    st.error("❌ Slack connection failed")
    
    # Status indicator
    if st.session_state.get('scheduler_running', False):
        st.info("⏰ Daily scheduler is running - will send news at 8 AM daily")
    else:
        st.info("⏸️ Daily scheduler is stopped - use 'Send News Now' for manual updates")

if __name__ == "__main__":
    # This allows the scheduler to be run standalone too
    scheduler = StreamlitScheduler()
    print("🚀 Starting Streamlit Scheduler...")
    
    # Test connection
    if scheduler.slack.test_connection():
        print("✅ Slack connection successful")
        
        # Run once
        print("📤 Sending test news...")
        scheduler.fetch_and_send_news()
    else:
        print("❌ Slack connection failed - check your secrets") 