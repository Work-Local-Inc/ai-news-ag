import streamlit as st
import pandas as pd
from news_fetcher import NewsAPI, HackerNewsFetcher, RSSFetcher, ArticleDeduplicator, AISummaryGenerator
from datetime import datetime
import time

st.set_page_config(
    page_title="AI News Scraper",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better card styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        border-radius: 20px;
        border: none;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-1px);
        transition: all 0.2s;
    }
    h3 a {
        text-decoration: none !important;
        color: #1f2937 !important;
    }
    h3 a:hover {
        color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI News Scraper")
st.markdown("*Stay updated with the latest AI developments from multiple sources*")

# Initialize session state for articles and summaries
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'summaries' not in st.session_state:
    st.session_state.summaries = {}

# Sidebar filters
st.sidebar.header("🔧 Filters")

# News type selection
news_type = st.sidebar.selectbox(
    "NewsAPI Type:",
    ["Everything", "Top Headlines"],
    help="Everything = all articles, Headlines = breaking news only"
)

news_sources = st.sidebar.multiselect(
    "Select Sources:",
    ["NewsAPI", "Hacker News", "Google News", "TechCrunch", "Ars Technica"],
    default=["NewsAPI", "Hacker News"],
    help="Multiple sources will be combined and deduplicated"
)

search_query = st.sidebar.text_input("Custom Search:", value="artificial intelligence")
num_articles = st.sidebar.slider("Articles per Source:", 5, 20, 10)

# AI Summary settings
st.sidebar.header("🧠 AI Summary Settings")
ai_provider = st.sidebar.selectbox(
    "Summary Provider:",
    ["None", "OpenAI (GPT-3.5)", "Google (Gemini)"],
    help="Requires API keys in .env file"
)

adhd_friendly = st.sidebar.checkbox(
    "🎯 ADHD-Friendly Summaries",
    value=True,
    help="Bullet points, key insights first, easy to scan"
)

# Filter keywords to exclude
exclude_keywords = st.sidebar.text_area(
    "Exclude Keywords (comma-separated):",
    placeholder="crypto, trump, war, sports",
    help="Articles containing these words will be filtered out"
)

# Similarity threshold for deduplication
similarity_threshold = st.sidebar.slider(
    "Duplicate Detection Sensitivity:",
    50, 95, 80,
    help="Higher = more strict duplicate detection"
)

if st.sidebar.button("🔄 Refresh News", type="primary"):
    with st.spinner("Fetching latest AI news from multiple sources..."):
        # Initialize fetchers
        news_api = NewsAPI()
        hn_fetcher = HackerNewsFetcher()
        rss_fetcher = RSSFetcher()
        ai_summarizer = AISummaryGenerator()
        
        all_articles = []
        
        # Fetch from NewsAPI if selected
        if "NewsAPI" in news_sources:
            with st.spinner("Fetching from NewsAPI..."):
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
                            'content': article.get('content', ''),
                            'score': 0  # NewsAPI doesn't have scores
                        })
        
        # Fetch from Hacker News if selected
        if "Hacker News" in news_sources:
            with st.spinner("Fetching from Hacker News..."):
                hn_stories = hn_fetcher.get_ai_stories(limit=num_articles)
                all_articles.extend(hn_stories)
        
        # Fetch from RSS if selected
        if any(source in news_sources for source in ["Google News", "TechCrunch", "Ars Technica"]):
            with st.spinner("Fetching from RSS feeds..."):
                rss_articles = rss_fetcher.fetch_rss_news()
                all_articles.extend(rss_articles)
        
        # Filter out excluded keywords
        if exclude_keywords:
            exclude_list = [kw.strip().lower() for kw in exclude_keywords.split(',') if kw.strip()]
            if exclude_list:
                original_count = len(all_articles)
                filtered_articles = []
                for article in all_articles:
                    title_lower = article['title'].lower()
                    desc_lower = article.get('description', '').lower()
                    
                    if not any(kw in title_lower or kw in desc_lower for kw in exclude_list):
                        filtered_articles.append(article)
                
                all_articles = filtered_articles
                if original_count > len(all_articles):
                    st.info(f"Filtered out {original_count - len(all_articles)} articles with excluded keywords")
        
        # Remove duplicates
        if len(all_articles) > 1:
            with st.spinner("Removing duplicates..."):
                all_articles = ArticleDeduplicator.remove_duplicates(all_articles, similarity_threshold)
        
        # Sort by publication date (newest first) and score
        all_articles.sort(key=lambda x: (x.get('score', 0), x.get('published', '')), reverse=True)
        
        # Store in session state
        st.session_state.articles = all_articles
        st.session_state.summaries = {}  # Clear old summaries
        
        st.success(f"✅ Found {len(all_articles)} unique articles from {len(news_sources)} sources!")

# Display articles
if st.session_state.articles:
    st.header(f"📰 Latest AI News ({len(st.session_state.articles)} articles)")
    
    # Add stats
    col1, col2, col3, col4 = st.columns(4)
    sources = [article.get('source', 'Unknown') for article in st.session_state.articles]
    source_counts = pd.Series(sources).value_counts()
    
    with col1:
        st.metric("Total Articles", len(st.session_state.articles))
    with col2:
        st.metric("Sources", len(source_counts))
    with col3:
        if source_counts.index.tolist():
            st.metric("Top Source", source_counts.index[0])
    with col4:
        avg_score = sum(article.get('score', 0) for article in st.session_state.articles) / len(st.session_state.articles)
        st.metric("Avg HN Score", f"{avg_score:.1f}")
    
    # Display articles in card layout
    for i, article in enumerate(st.session_state.articles):
        
        # Create card container with custom CSS styling
        with st.container():
            # Card styling
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                margin: 1rem 0;
                border-radius: 10px;
                border-left: 4px solid #FF6B6B;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border: 1px solid #E1E4E8;
            ">
            """, unsafe_allow_html=True)
            
            # Article title (clickable)
            st.markdown(f"### [📄 {article['title']}]({article['url']})")
            
            # Source and metadata row
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.markdown(f"**🏢 {article.get('source', 'Unknown')}**")
            with col2:
                st.markdown(f"📅 {article.get('published', 'Unknown')[:10]}")
            with col3:
                if article.get('score', 0) > 0:
                    st.markdown(f"⭐ {article['score']} pts")
            with col4:
                st.markdown(f"#{i+1}")
            
            # Article description/preview
            if article.get('description'):
                description = article['description'][:200] + "..." if len(article['description']) > 200 else article['description']
                st.markdown(f"*{description}*")
            
            # Action buttons row
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # AI Summary section
                if ai_provider != "None":
                    summary_key = f"summary_{i}"
                    
                    if summary_key in st.session_state.summaries:
                        st.markdown("**🧠 AI Summary:**")
                        st.info(st.session_state.summaries[summary_key])
                    else:
                        if st.button(f"🤖 Get AI Summary", key=f"summarize_{i}", type="secondary"):
                            with st.spinner("Generating AI summary..."):
                                title = article['title']
                                description = article.get('description', '')
                                content = article.get('content', '')
                                
                                if ai_provider == "OpenAI (GPT-3.5)":
                                    summary = ai_summarizer.summarize_with_openai(title, description, content, adhd_friendly)
                                elif ai_provider == "Google (Gemini)":
                                    summary = ai_summarizer.summarize_with_gemini(title, description, content, adhd_friendly)
                                else:
                                    summary = "AI summary not available"
                                
                                st.session_state.summaries[summary_key] = summary
                                st.rerun()
            
            with col2:
                # Read full article button
                st.markdown(f"[📖 Read Full]({article['url']})")
            
            with col3:
                # Share button (placeholder)
                if st.button("🔗 Share", key=f"share_{i}"):
                    st.write("📋 URL copied to clipboard!")
                    st.code(article['url'])
            
            # Close card div
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add some spacing between cards
            st.markdown("<br>", unsafe_allow_html=True)

else:
    st.info("👆 Click 'Refresh News' to load articles from your selected sources")
    
    # Show available sources info
    st.markdown("### 📡 Available Sources")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **NewsAPI**
        - Professional news sources
        - 1,000 requests/day (free)
        - Real-time updates
        
        **Hacker News**
        - Tech community favorites
        - No API limits
        - Story scores included
        """)
    
    with col2:
        st.markdown("""
        **RSS Feeds**
        - Google News AI search
        - TechCrunch AI coverage
        - Ars Technica tech news
        
        **AI Summaries**
        - OpenAI GPT-3.5 powered
        - Google Gemini powered
        - Requires API keys
        """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("*Built with Streamlit*")
with col2:
    st.markdown("*Powered by NewsAPI & Hacker News*")
with col3:
    st.markdown("*AI Summaries via OpenAI/Gemini*")
