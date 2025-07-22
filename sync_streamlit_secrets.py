#!/usr/bin/env python3
"""
Sync Streamlit secrets with .env file for Slack integration
Run this if you have API keys in Streamlit secrets that you want to use locally
"""

import os
import streamlit as st
from pathlib import Path

def sync_secrets_to_env():
    """Copy Streamlit secrets to .env file for local development"""
    
    print("🔄 Syncing Streamlit secrets to .env file...")
    
    # Read current .env file
    env_file = Path('.env')
    env_lines = []
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Check what secrets are available in Streamlit
    available_secrets = {}
    
    try:
        if hasattr(st, 'secrets'):
            print("📋 Checking Streamlit secrets...")
            
            # Common secret keys to check
            secret_keys = [
                'NEWS_API_KEY',
                'OPENAI_API_KEY', 
                'GOOGLE_API_KEY',
                'GEMINI_API_KEY'
            ]
            
            for key in secret_keys:
                try:
                    value = st.secrets.get(key)
                    if value and value != 'your_key_here':
                        available_secrets[key] = value
                        print(f"   ✅ Found {key}")
                    else:
                        print(f"   ⚠️ {key} not found or placeholder")
                except:
                    print(f"   ⚠️ {key} not accessible")
        else:
            print("⚠️ Streamlit secrets not available (run from Streamlit app)")
            
    except Exception as e:
        print(f"❌ Error accessing Streamlit secrets: {e}")
    
    if available_secrets:
        print(f"\n📝 Updating .env file with {len(available_secrets)} secrets...")
        
        # Update .env file
        updated_lines = []
        updated_keys = set()
        
        for line in env_lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0]
                if key in available_secrets:
                    updated_lines.append(f"{key}={available_secrets[key]}\n")
                    updated_keys.add(key)
                    print(f"   🔄 Updated {key}")
                else:
                    updated_lines.append(line + '\n')
            else:
                updated_lines.append(line + '\n')
        
        # Add any new keys
        for key, value in available_secrets.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}\n")
                print(f"   ➕ Added {key}")
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated successfully!")
        
    else:
        print("⚠️ No Streamlit secrets found to sync")
    
    return available_secrets

def show_current_status():
    """Show current status of all API keys"""
    print("\n📊 Current API Key Status:")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    keys_to_check = [
        ('NEWS_API_KEY', 'NewsAPI (required for news)'),
        ('SLACK_BOT_TOKEN', 'Slack Bot (required for Slack)'),
        ('SLACK_CHANNEL', 'Slack Channel'),
        ('OPENAI_API_KEY', 'OpenAI (optional for summaries)'),
        ('GOOGLE_API_KEY', 'Google Gemini (optional for summaries)'),
        ('SLACK_WEBHOOK_URL', 'Slack Webhook (alternative to bot)')
    ]
    
    for key, description in keys_to_check:
        value = os.getenv(key)
        if value and value not in ['your_key_here', 'your_openai_key_here', 'your_gemini_key_here']:
            status = "✅ Set"
            if key in ['SLACK_BOT_TOKEN', 'NEWS_API_KEY', 'OPENAI_API_KEY']:
                # Partially hide sensitive keys
                display_value = f"({value[:8]}...{value[-4:]})" if len(value) > 12 else "(set)"
            else:
                display_value = f"({value})"
        else:
            status = "❌ Missing"
            display_value = ""
        
        print(f"   {status} {key:<20} {description} {display_value}")

if __name__ == "__main__":
    print("🔐 Streamlit Secrets & .env Sync Tool")
    print("=" * 50)
    
    # Show current status
    show_current_status()
    
    # Try to sync if running in Streamlit context
    try:
        import streamlit as st
        if st._is_running_with_streamlit:
            sync_secrets_to_env()
    except:
        print("\n💡 To sync Streamlit secrets:")
        print("   1. Add this to your Streamlit app temporarily:")
        print("   2. import sync_streamlit_secrets")
        print("   3. sync_streamlit_secrets.sync_secrets_to_env()")
        print("   4. Run your Streamlit app")
    
    print("\n🚀 Ready for Slack integration!") 