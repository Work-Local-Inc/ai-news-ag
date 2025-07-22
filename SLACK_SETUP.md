# 🚀 Slack Integration Setup

This guide will help you set up daily automated AI news updates to your Slack channel.

## 📋 Prerequisites

1. Admin access to a Slack workspace
2. Python environment with the required dependencies

## 🔧 Setup Options

You have two ways to integrate with Slack:

### Option 1: Slack Webhook (Easiest)
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "AI News Daily") and select your workspace
4. Go to "Incoming Webhooks" and activate them
5. Click "Add New Webhook to Workspace"
6. Choose the channel where you want news posted
7. Copy the webhook URL

### Option 2: Slack Bot (More Features)
1. Follow steps 1-3 from Option 1
2. Go to "OAuth & Permissions"
3. Add these scopes under "Bot Token Scopes":
   - `chat:write`
   - `files:write`
4. Install the app to your workspace
5. Copy the "Bot User OAuth Token"

## 🔐 Environment Variables

Add these to your `.env` file:

```bash
# For Webhook (Option 1)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# For Bot (Option 2) - Optional but recommended
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL=#ai-news

# Your existing API keys
NEWS_API_KEY=your_news_api_key
OPENAI_API_KEY=your_openai_key  # Optional for AI summaries
GOOGLE_API_KEY=your_gemini_key  # Optional for AI summaries
```

## 🏃‍♂️ Running the Scheduler

### Method 1: Python Script (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Test the connection
python daily_scheduler.py

# Run continuously (keeps running until stopped)
python daily_scheduler.py
```

### Method 2: Cron Job (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line for 8 AM daily:
0 8 * * * cd /path/to/your/project && python daily_scheduler.py
```

### Method 3: Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Daily" at 8:00 AM
4. Set action to start `python.exe` with argument `daily_scheduler.py`

## 🧪 Testing

1. **Test Slack Connection:**
   ```bash
   python -c "from daily_scheduler import DailyNewsScheduler; DailyNewsScheduler().test_slack_connection()"
   ```

2. **Send Test News Update:**
   ```bash
   python -c "from daily_scheduler import DailyNewsScheduler; DailyNewsScheduler().send_daily_update()"
   ```

## 📱 What the Slack Message Looks Like

Your daily message will include:
- 🤖 **Header**: "AI News Daily - [Date]"
- 📊 **Stats**: Source breakdown (Hacker News vs News APIs)
- 📰 **Articles**: Up to 10 top stories with:
  - Clickable titles
  - Descriptions
  - Source badges (🟢 Hacker News, 🔵 Other sources)
  - Publication dates
  - Article images (when available)

## 🔧 Customization

Edit `daily_scheduler.py` to customize:
- **Timing**: Change `"08:00"` to your preferred time
- **Article count**: Modify `limit=10` parameters
- **Search terms**: Update the NewsAPI query
- **Message format**: Modify `slack_notifier.py`

## 🚨 Troubleshooting

**Common Issues:**
1. **"No Slack webhook URL configured"**: Check your `.env` file
2. **"Permission denied"**: Make sure your bot has the right scopes
3. **"Channel not found"**: Use channel ID instead of name (e.g., `C1234567890`)
4. **Rate limits**: Slack has rate limits; the script handles this automatically

## 🌟 Pro Tips

1. **Multiple Channels**: Set up different webhooks for different teams
2. **Custom Queries**: Modify the NewsAPI search terms for specific topics
3. **AI Summaries**: Enable OpenAI/Gemini integration for article summaries
4. **Cloud Deployment**: Deploy to AWS Lambda, Google Cloud Functions, or Heroku for 24/7 operation

## 📞 Support

If you run into issues:
1. Check the console output for error messages
2. Verify your environment variables
3. Test the Slack connection first
4. Make sure all dependencies are installed

Happy news sharing! 🎉 