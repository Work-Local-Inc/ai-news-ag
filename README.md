# AI News Scraper 🤖

A Streamlit app that aggregates AI news from multiple sources and provides AI-powered summaries.

## 🚀 Live Demo
Deploy to Streamlit Cloud: [![Deploy](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

# AI News Scraper 🤖

A comprehensive Streamlit app that aggregates AI news from multiple sources, removes duplicates, and provides AI-powered summaries.

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

3. **Get your NewsAPI key:**
   - Sign up at [NewsAPI.org](https://newsapi.org/register) (free)
   - Copy `.env.example` to `.env`
   - Add your API key to `.env`

4. **Run the app:**
```bash
streamlit run app.py
```

## 🧪 Test API Connection

```bash
python news_fetcher.py
```

## 🚀 Deploy to Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repo
4. Add your `NEWS_API_KEY` to the secrets section
5. Deploy!

## 📝 TODO

- [ ] Fix RSS feed parsing
- [ ] Add AI summary integration
- [ ] Add article sentiment analysis
- [ ] Export to PDF/CSV
- [ ] Email digest feature
