#!/usr/bin/env bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MUserBot Pro — 1-Click Auto Setup & Startup Script
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "=================================================="
echo "  🚀 Starting MUserBot Pro Master Engine"
echo "=================================================="

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed! Please install Python 3.10+ first."
    exit 1
fi

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv || virtualenv venv || true
fi

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install / update requirements
echo "📥 Checking and installing required dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚠️ .env file not found. Creating from .env.example..."
        cp .env.example .env
        echo "❗ Please edit .env with your real BOT_TOKEN, API_ID, and API_HASH before starting!"
    fi
fi

# Run Master Bot
echo "🟢 Launching MUserBot Master Bot..."
exec python3 reuserbot/main.py
