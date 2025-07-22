#!/bin/bash
# Daily AI News Scheduler Startup Script
# This script starts the daily news scheduler that will send updates to Slack at 8 AM

echo "🚀 Starting AI News Daily Scheduler..."

# Change to the project directory
cd "$(dirname "$0")"

# Make sure we have the .env file
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your Slack and API credentials."
    exit 1
fi

# Check if python3 is available
if ! command -v /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 &> /dev/null; then
    echo "❌ Error: Python 3.13 not found!"
    echo "Please install Python 3.13 or update the path in this script."
    exit 1
fi

echo "📋 Configuration:"
echo "   - Scheduled time: 8:00 AM daily"
echo "   - Log file: scheduler.log"
echo "   - Press Ctrl+C to stop"
echo ""

# Start the scheduler with logging
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 daily_scheduler.py 2>&1 | tee scheduler.log 