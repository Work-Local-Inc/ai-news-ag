import streamlit as st
import pandas as pd
from news_fetcher import NewsAPI, HackerNewsFetcher, RSSFetcher, ArticleDeduplicator, AISummaryGenerator, ArticleImageExtractor
from datetime import datetime
import time

st.set_page_config(
    page_title="AI News Scraper",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for proper card styling with borders and images
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    
    /* Card container styling */
    .card-container {
        background: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        padding: 0;
        margin-bottom: 1.5rem;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.95);
    }
    
    .card-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }
    
    .card-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 12px 12px 0 0;
    }
    
    .card-content {
        padding: 1rem;
    }
    
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        width: 100%;
        margin: 0.25rem 0;
    }
    
    h3 {
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    /* Article title styling - look like headlines, not links */
    .article-title {
        color: #1f2937 !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        line-height: 1.4 !important;
        display: block !important;
        margin-bottom: 8px !important;
    }
    
    .article-title:hover {
        color: #4f46e5 !important;
        text-decoration: none !important;
        transform: none !important;
    }
    
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .hn-badge {
        background: #ff6600;
        color: white;
    }
    
    .other-badge {
        background: #3b82f6;
        color: white;
    }
    
    /* Clean article title links */
    a.article-title {
        text-decoration: none !important;
        color: #1f2937 !important;
        font-weight: 600 !important;
        transition: color 0.2s ease;
    }
    a.article-title:hover {
        color: #3b82f6 !important;
        text-decoration: none !important;
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
    
    # Display articles in proper card grid layout with images
    
    # Create cards in a responsive grid (4 per row for compact cards)
    cols_per_row = 4  # Four compact cards per row
    
    for i in range(0, len(st.session_state.articles), cols_per_row):
        row_articles = st.session_state.articles[i:i+cols_per_row]
        cols = st.columns(cols_per_row, gap="small")
        
        for idx, article in enumerate(row_articles):
            with cols[idx]:
                # Create individual compact card container with image
                with st.container():
                    
                    # Get article image
                    if 'image_url' not in article:
                        # Try to extract real image first, fallback to placeholder
                        try:
                            article['image_url'] = ArticleImageExtractor.get_article_image(
                                article['url'], 
                                article['title']
                            )
                        except:
                            article['image_url'] = ArticleImageExtractor.get_source_specific_image(
                                article.get('source', 'Unknown'),
                                article['title']
                            )
                    
                    # Display compact card image
                    try:
                        st.image(article['image_url'], use_container_width=True)
                    except:
                        # Fallback to a simple colored placeholder (smaller)
                        st.markdown(f"""
                        <div style="
                            height: 120px; 
                            background: linear-gradient(45deg, #667eea, #764ba2); 
                            border-radius: 6px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-size: 18px;
                            margin-bottom: 0.5rem;
                        ">📰</div>
                        """, unsafe_allow_html=True)
                    
                    # Compact card header with clean title (styled link)
                    st.markdown(f"""
                    <a href="{article['url']}" target="_blank" class="article-title">
                        {article['title'][:40]}{'...' if len(article['title']) > 40 else ''}
                    </a>
                    """, unsafe_allow_html=True)
                    """, unsafe_allow_html=True)
                    
                    # Source badge (compact)
                    if article.get('source') == "Hacker News":
                        st.markdown("🟢 **HN**")
                        if article.get('score', 0) > 0:
                            st.caption(f"⭐ {article['score']} pts")
                    else:
                        st.markdown(f"🔵 **{article.get('source', 'Unknown')[:8]}**")
                    
                    # Date (compact)
                    st.caption(f"📅 {article.get('published', 'Unknown')[:10]}")
                    
                    # Description preview (much shorter for compact cards)
                    if article.get('description'):
                        description = article['description'][:60] + "..." if len(article['description']) > 60 else article['description']
                        st.caption(description)
                    
                    # Compact action buttons
                    if st.button(f"📖", key=f"read_{i}_{idx}", use_container_width=True, help="Read Article"):
                        st.balloons()
                        st.markdown(f"[🔗 {article['url']}]({article['url']})")
                    
                    # AI Summary section (compact)
                    if ai_provider != "None":
                        summary_key = f"summary_{i}_{idx}"
                        
                        if summary_key in st.session_state.summaries:
                            st.success("🧠")
                            with st.expander("Summary", expanded=False):
                                st.markdown(st.session_state.summaries[summary_key])
                        else:
                            if st.button(f"🤖", key=f"summarize_{i}_{idx}", use_container_width=True, help="AI Summary"):
                                with st.spinner("🧠"):
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
                
                # Add visual separation between cards
                st.markdown("---")
        
        # Add space between rows
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
