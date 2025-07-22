    # Display articles in proper card grid layout with images
    
    # Create cards in a responsive grid
    cols_per_row = 2  # Two cards per row
    
    for i in range(0, len(st.session_state.articles), cols_per_row):
        row_articles = st.session_state.articles[i:i+cols_per_row]
        cols = st.columns(cols_per_row, gap="medium")
        
        for idx, article in enumerate(row_articles):
            with cols[idx]:
                # Create modern card with custom styling
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 16px;
                    padding: 0;
                    margin-bottom: 2rem;
                    overflow: hidden;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                ">
                """, unsafe_allow_html=True)
                
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
                    
                    # Display card image with rounded corners
                    try:
                        st.markdown(f"""
                        <img src="{article['image_url']}" style="
                            width: 100%;
                            height: 200px;
                            object-fit: cover;
                            border-radius: 16px 16px 0 0;
                            margin-bottom: 0;
                        ">
                        """, unsafe_allow_html=True)
                    except:
                        # Fallback to a beautiful gradient placeholder
                        st.markdown(f"""
                        <div style="
                            height: 200px; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
                            border-radius: 16px 16px 0 0;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-size: 48px;
                            margin-bottom: 0;
                            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                        ">📰</div>
                        """, unsafe_allow_html=True)
                    
                    # Card content with padding
                    st.markdown('<div style="padding: 1.5rem;">', unsafe_allow_html=True)
                    
                    # Card title - large, white, clickable
                    title_text = article['title'][:80] + "..." if len(article['title']) > 80 else article['title']
                    st.markdown(f"""
                    <h2 style="
                        color: #ffffff;
                        font-size: 1.4rem;
                        font-weight: 600;
                        line-height: 1.3;
                        margin: 0 0 1rem 0;
                        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                    ">
                        <a href="{article['url']}" target="_blank" style="
                            color: #ffffff;
                            text-decoration: none;
                            transition: color 0.2s ease;
                        " onmouseover="this.style.color='#60a5fa'" onmouseout="this.style.color='#ffffff'">
                            {title_text}
                        </a>
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    # Source badge and score in a nice row
                    source_text = "Hacker News" if article.get('source') == "Hacker News" else article.get('source', 'Unknown')
                    source_emoji = "🟢" if article.get('source') == "Hacker News" else "🔵"
                    score_text = f" • {article.get('score', 0)} pts" if article.get('score', 0) > 0 else ""
                    
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 0.75rem;
                        color: #cbd5e1;
                        font-size: 0.9rem;
                    ">
                        <span style="
                            background: rgba(255, 255, 255, 0.1);
                            padding: 0.25rem 0.75rem;
                            border-radius: 20px;
                            font-weight: 500;
                        ">
                            {source_emoji} {source_text}{score_text}
                        </span>
                        <span>📅 {article.get('published', 'Unknown')[:10]}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Description with better styling
                    if article.get('description'):
                        description = article['description'][:120] + "..." if len(article['description']) > 120 else article['description']
                        st.markdown(f"""
                        <p style="
                            color: #94a3b8;
                            font-size: 0.95rem;
                            line-height: 1.5;
                            margin: 0 0 1.5rem 0;
                        ">{description}</p>
                        """, unsafe_allow_html=True)
                    
                    # Modern action buttons
                    button_col1, button_col2 = st.columns(2)
                    
                    with button_col1:
                        if st.button(f"📖 Read", key=f"read_{i}_{idx}", use_container_width=True):
                            st.balloons()
                            st.markdown(f"Opening: {article['url']}")
                    
                    with button_col2:
                        if st.button("📤 Share", key=f"share_{i}_{idx}", use_container_width=True):
                            st.code(article['url'], language=None)
                            st.success("📋 URL ready to copy!")
                    
                    # AI Summary section with modern styling
                    if ai_provider != "None":
                        summary_key = f"summary_{i}_{idx}"
                        
                        if summary_key in st.session_state.summaries:
                            st.markdown(f"""
                            <div style="
                                background: rgba(34, 197, 94, 0.1);
                                border: 1px solid rgba(34, 197, 94, 0.3);
                                border-radius: 12px;
                                padding: 1rem;
                                margin-top: 1rem;
                            ">
                                <div style="
                                    color: #10b981;
                                    font-weight: 600;
                                    margin-bottom: 0.5rem;
                                    display: flex;
                                    align-items: center;
                                    gap: 0.5rem;
                                ">
                                    🧠 AI Summary
                                </div>
                                <div style="color: #e2e8f0; line-height: 1.6;">
                                    {st.session_state.summaries[summary_key]}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
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
                    
                    # Close card content padding
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Close card container
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Add space between rows
        st.markdown("<br>", unsafe_allow_html=True)
