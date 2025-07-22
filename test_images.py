import streamlit as st

st.title("🖼️ Testing Article Images")

# Test the image extractor
from news_fetcher import ArticleImageExtractor

# Test article
test_url = "https://news.ycombinator.com/item?id=1"
test_title = "DaisyUI: Tailwind CSS Components"

# Test image extraction
img_extractor = ArticleImageExtractor()

st.header("Testing Placeholder Images")

# Test different strategies
col1, col2 = st.columns(2)

with col1:
    st.subheader("Source-specific (HN)")
    hn_image = img_extractor.get_source_specific_image("Hacker News", test_title)
    st.image(hn_image, caption="Hacker News themed", use_container_width=True)

with col2:
    st.subheader("Generic Placeholder") 
    generic_image = img_extractor.get_placeholder_image(test_title, test_url)
    st.image(generic_image, caption="Generic tech themed", use_container_width=True)

st.success("✅ Image system working!")
