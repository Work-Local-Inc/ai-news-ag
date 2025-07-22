import streamlit as st
import pandas as pd
from news_fetcher import NewsAPI, RSSFetcher
from datetime import datetime
import time

st.set_page_config(
    page_title="AI News Scraper",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI News Scraper")
st.markdown("*Stay updated with the latest AI developments*")

# Sidebar filters
st.sidebar.header("Filters")

# News type selection
news_type = st.sidebar.selectbox(
    "News Type:",
    ["Everything", "Top Headlines"],
    help="Everything = all articles, Headlines = breaking news only"
)

news_sources = st.sidebar.multiselect(
    "Select Sources:",
    ["NewsAPI", "Google News", "TechCrunch", "Ars Technica"],
    default=["NewsAPI"]
)

search_query = st.sidebar.text_input("Custom Search:", value="artificial intelligence")
num_articles = st.sidebar.slider("Number of Articles:", 5, 50, 20)

# Filter keywords to exclude
exclude_keywords = st.sidebar.text_area(
    "Exclude Keywords (comma-separated):",
    placeholder="crypto, trump, war"
)

if st.sidebar.button("🔄 Refresh News"):
    with st.spinner("Fetching latest news..."):
        # Initialize fetchers
        news_api = NewsAPI()
        rss_fetcher = RSSFetcher()
        
        all_articles = []
        
        # Fetch from NewsAPI if selected
        if "NewsAPI" in news_sources:
            if news_type == "Top Headlines":
                news_data = news_api.get_top_ai_headlines(page_size=num_articles)
            else:
                news_data = news_api.get_ai_news(query=search_query, page_size=num_articles)
            
            if news_data and news_data.get('status') == 'ok' and 'articles' in news_data:
                for article in news_data['articles']:
                    all_articles.append({
                        'title': article['title'],
                        'url': article['url'],
                        'source': article['source']['name'],
                        'published': article['publishedAt'],
                        'description': article.get('description', ''),
                        'content': article.get('content', '')
                    })
        
        # Fetch from RSS if selected
        if any(source in news_sources for source in ["Google News", "TechCrunch", "Ars Technica"]):
            rss_articles = rss_fetcher.fetch_rss_news()
            all_articles.extend(rss_articles)
        
        # Filter out excluded keywords
        if exclude_keywords:
            exclude_list = [kw.strip().lower() for kw in exclude_keywords.split(',')]
            filtered_articles = []
            for article in all_articles:
                title_lower = article['title'].lower()
                desc_lower = article.get('description', '').lower()
                
                if not any(kw in title_lower or kw in desc_lower for kw in exclude_list):
                    filtered_articles.append(article)
            
            all_articles = filtered_articles
        
        # Store in session state
        st.session_state.articles = all_articles
        st.success(f"✅ Found {len(all_articles)} articles!")

# Display articles
if 'articles' in st.session_state and st.session_state.articles:
    st.header(f"📰 Latest Articles ({len(st.session_state.articles)})")
    
    for i, article in enumerate(st.session_state.articles):
        with st.expander(f"{article['title'][:100]}..."):
            st.markdown(f"**Source:** {article.get('source', 'Unknown')}")
            st.markdown(f"**Published:** {article.get('published', 'Unknown')}")
            st.markdown(f"**URL:** {article['url']}")
            
            if article.get('description'):
                st.markdown(f"**Description:** {article['description']}")
            
            # Add summarize button placeholder for later
            if st.button(f"🤖 Summarize", key=f"summarize_{i}"):
                st.info("AI Summary feature coming soon!")

else:
    st.info("👆 Click 'Refresh News' to load articles")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and powered by NewsAPI + RSS feeds*")
