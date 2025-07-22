    # Display articles in proper card grid layout with images
    
    # Create cards in a responsive grid
    cols_per_row = 2  # Two cards per row
    
    for i in range(0, len(st.session_state.articles), cols_per_row):
        row_articles = st.session_state.articles[i:i+cols_per_row]
        cols = st.columns(cols_per_row, gap="medium")
        
        for idx, article in enumerate(row_articles):
            with cols[idx]:
                # Create individual card container with image
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
                    
                    # Display card image
                    try:
                        st.image(article['image_url'], use_container_width=True)
                    except:
                        # Fallback to a simple colored placeholder
                        st.markdown(f"""
                        <div style="
                            height: 150px; 
                            background: linear-gradient(45deg, #667eea, #764ba2); 
                            border-radius: 8px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-size: 24px;
                            margin-bottom: 1rem;
                        ">📰</div>
                        """, unsafe_allow_html=True)
                    
                    # Card header with title
                    st.markdown(f"""
                    <h2 style="color: white; font-size: 1.5rem; margin-bottom: 0.5rem;">
                        <a href="{article['url']}" target="_blank" style="color: white; text-decoration: none;">
                            {article['title'][:60]}...
                        </a>
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    # Source badge and score row
                    source_col, score_col = st.columns([2, 1])
                    with source_col:
                        if article.get('source') == "Hacker News":
                            st.markdown("🟢 **Hacker News**")
                        else:
                            st.markdown(f"🔵 **{article.get('source', 'Unknown')}**")
                    
                    with score_col:
                        if article.get('score', 0) > 0:
                            st.metric("", f"{article['score']} pts", "HN")
                    
                    # Date
                    st.caption(f"📅 {article.get('published', 'Unknown')[:10]}")
                    
                    # Description preview (shorter for image cards)
                    if article.get('description'):
                        description = article['description'][:100] + "..." if len(article['description']) > 100 else article['description']
                        st.caption(description)
                    
                    # Action buttons - stacked vertically for cards
                    if st.button(f"📖 Read Article", key=f"read_{i}_{idx}", use_container_width=True):
                        st.balloons()
                        st.markdown(f"Opening: {article['url']}")
                    
                    # AI Summary section
                    if ai_provider != "None":
                        summary_key = f"summary_{i}_{idx}"
                        
                        if summary_key in st.session_state.summaries:
                            st.success("🧠 AI Summary")
                            st.markdown(st.session_state.summaries[summary_key])
                        else:
                            if st.button(f"🤖 AI Summary", key=f"summarize_{i}_{idx}", use_container_width=True):
                                with st.spinner("🧠 Generating..."):
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
                    
                    # Share button
                    if st.button("📤 Share", key=f"share_{i}_{idx}", use_container_width=True):
                        st.code(article['url'], language=None)
                        st.success("📋 URL ready to copy!")
                
                # Add visual separation between cards
                st.markdown("---")
        
        # Add space between rows
        st.markdown("<br>", unsafe_allow_html=True)
