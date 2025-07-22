#!/usr/bin/env python3

"""
Quick test for ADHD-friendly summaries
"""

from news_fetcher import AISummaryGenerator

def test_adhd_summary():
    summarizer = AISummaryGenerator()
    
    # Test article
    title = "OpenAI Releases GPT-5 with Revolutionary Multimodal Capabilities"
    description = "The latest language model can process text, images, video, and audio simultaneously, marking a significant leap in AI development."
    content = "OpenAI announced today the release of GPT-5, featuring unprecedented multimodal capabilities that allow the model to understand and generate content across text, images, video, and audio formats simultaneously..."
    
    print("=== REGULAR SUMMARY ===")
    regular = summarizer.summarize_with_openai(title, description, content, adhd_friendly=False)
    print(regular)
    
    print("\n=== ADHD-FRIENDLY SUMMARY ===")
    adhd = summarizer.summarize_with_openai(title, description, content, adhd_friendly=True)
    print(adhd)

if __name__ == "__main__":
    test_adhd_summary()
