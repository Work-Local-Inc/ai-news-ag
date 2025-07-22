#!/usr/bin/env python3
"""
Quick Slack integration test script
Run this after setting up your Slack bot permissions
"""

import os
from dotenv import load_dotenv
from slack_notifier import SlackNotifier

def main():
    load_dotenv()
    
    print("🔧 Slack Configuration Check:")
    print(f"   Bot Token: {'✅ Found' if os.getenv('SLACK_BOT_TOKEN') else '❌ Missing'}")
    print(f"   Channel: {os.getenv('SLACK_CHANNEL', '#ai-news')}")
    print()
    
    if not os.getenv('SLACK_BOT_TOKEN'):
        print("❌ Please add SLACK_BOT_TOKEN to your .env file")
        return
    
    print("🧪 Testing Slack Connection...")
    slack = SlackNotifier()
    
    # Test connection
    if slack.test_connection():
        print("✅ SUCCESS! Test message sent to Slack!")
        print("📱 Check your Slack channel for the test message")
        
        # Test with sample news data
        print("\n📰 Testing with sample news data...")
        sample_articles = [
            {
                'title': 'Test AI News Article',
                'description': 'This is a test article to verify Slack integration is working correctly.',
                'url': 'https://example.com/test-article',
                'source': 'Test Source',
                'published': '2024-01-01',
                'score': 42
            }
        ]
        
        stats = {'hacker_news_count': 0, 'news_api_count': 1}
        
        if slack.send_daily_news(sample_articles, stats):
            print("✅ Sample news sent successfully!")
        else:
            print("❌ Failed to send sample news")
            
    else:
        print("❌ Connection failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure your bot is invited to the channel:")
        print("   - Go to your Slack channel")
        print("   - Type: /invite @YourBotName")
        print("2. Check bot permissions at https://api.slack.com/apps")
        print("   - Required scopes: chat:write, chat:write.public, channels:read")
        print("3. Try using Channel ID instead of name:")
        print("   - Right-click channel > Copy link")
        print("   - Update .env: SLACK_CHANNEL=C1234567890")

if __name__ == "__main__":
    main() 