# AI News Scraper 🤖

A Streamlit app that aggregates AI news from multiple sources and provides AI-powered summaries.

## 🚀 Live Demo
Deploy to Streamlit Cloud: [![Deploy](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## ✨ Features

- ✅ NewsAPI integration (1000 free requests/day)
- ✅ Multiple source filtering
- ✅ Keyword exclusion filters  
- ✅ Clean, responsive UI
- 🚧 RSS feeds (Google News, TechCrunch, Ars Technica) 
- 🚧 AI summaries (OpenAI/Gemini integration)

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
