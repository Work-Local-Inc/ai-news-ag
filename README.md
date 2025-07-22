# AI News Scraper 🤖

A comprehensive Streamlit app that aggregates AI news from multiple sources, removes duplicates, provides AI-powered summaries, and sends daily updates to Slack.

## 🚀 Live Demo
Deploy to Streamlit Cloud: [![Deploy](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## ✨ Features

### 📡 **Multiple News Sources**
- ✅ **NewsAPI** - Professional news sources (1000 free requests/day)
- ✅ **Hacker News** - Tech community favorites with story scores
- ✅ **RSS Feeds** - Google News, TechCrunch, Ars Technica
- ✅ **Smart Deduplication** - Removes similar articles using fuzzy matching

### 🤖 **AI-Powered Summaries**
- ✅ **OpenAI GPT-3.5** integration for article summaries
- ✅ **Google Gemini** integration for article summaries  
- ✅ **2-3 sentence summaries** focusing on key insights

### 🔧 **Advanced Filtering**
- ✅ Keyword exclusion (filter out crypto, politics, etc.)
- ✅ Source selection (mix and match sources)
- ✅ Configurable duplicate sensitivity
- ✅ Articles per source control

### 📊 **Analytics Dashboard**
- ✅ Source distribution metrics
- ✅ Hacker News story scores
- ✅ Publication timestamps
- ✅ Article count tracking

### 📱 **Slack Integration**
- ✅ **Daily automated updates** - Sends curated news at 8 AM
- ✅ **Beautiful formatted messages** - Rich blocks with images and links
- ✅ **Source attribution** - Clear badges for Hacker News vs other sources
- ✅ **Easy setup** - Bot token or webhook integration

## 🛠️ Setup

1. **Clone the repo:**
```bash
git clone https://github.com/Work-Local-Inc/ai-news-ag.git
cd ai-news-ag
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Get your API keys:**
   - **NewsAPI:** Sign up at [NewsAPI.org](https://newsapi.org/register) (free, 1000/day)
   - **OpenAI (optional):** Get key at [platform.openai.com](https://platform.openai.com/api-keys) (paid)
   - **Google Gemini (optional):** Get key at [ai.google.dev](https://ai.google.dev/) (has free tier!)
   - **Slack (optional):** Set up bot at [api.slack.com/apps](https://api.slack.com/apps) - see `SLACK_SETUP.md`
   - Add your API keys to `.env`

4. **Run the app:**
```bash
streamlit run app.py
```

## 🧪 Testing

**Test API connections:**
```bash
python news_fetcher.py
```

**Test Slack integration:**
```bash
./test_slack.py
```

**Start daily scheduler:**
```bash
./start_daily_scheduler.sh
```

## 🚀 Deploy to Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repo
4. Add your `NEWS_API_KEY` to the secrets section
5. Deploy!

## 📱 Slack Daily Updates

Set up automated daily news updates to your Slack workspace:

1. **Setup:** Follow the detailed guide in `SLACK_SETUP.md`
2. **Test:** Run `./test_slack.py` to verify connection
3. **Schedule:** Run `./start_daily_scheduler.sh` for 8 AM daily updates
4. **Deploy:** Set up on a server or cloud function for 24/7 operation

## 📁 Project Structure

```
ai-news-ag/
├── app.py                 # Main Streamlit app
├── news_fetcher.py        # News aggregation logic
├── card_layout.py         # UI card components
├── slack_notifier.py      # Slack integration
├── daily_scheduler.py     # Automated scheduling
├── test_slack.py          # Slack testing script
├── start_daily_scheduler.sh # Easy startup script
├── SLACK_SETUP.md         # Detailed Slack setup guide
└── requirements.txt       # Python dependencies
```

## 📝 TODO

- [x] Multiple news sources integration
- [x] AI-powered summaries  
- [x] Smart deduplication
- [x] Modern card-based UI
- [x] Slack daily updates
- [ ] Export to PDF/CSV
- [ ] Email digest feature
- [ ] Article sentiment analysis
- [ ] Mobile app version
