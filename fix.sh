#!/bin/bash

# Quick Fix Script for AI Agent Briefer
# This script helps diagnose and fix common issues

echo "🔧 AI Agent Briefer - Quick Fix Script"
echo "======================================="
echo ""

# Check if .env file exists
echo "1️⃣ Checking .env file..."
if [ -f ".env" ]; then
    echo "   ✅ .env file found"
    
    # Check for required keys
    required_keys=("GOOGLE_API_KEY" "SERPER_API_KEY" "TELEGRAM_BOT_TOKEN" "TELEGRAM_CHAT_ID")
    missing_keys=()
    
    for key in "${required_keys[@]}"; do
        if ! grep -q "^$key=" .env; then
            missing_keys+=("$key")
        fi
    done
    
    if [ ${#missing_keys[@]} -eq 0 ]; then
        echo "   ✅ All required API keys present"
    else
        echo "   ⚠️  Missing API keys: ${missing_keys[*]}"
        echo "      Add them to your .env file"
    fi
else
    echo "   ❌ .env file not found"
    echo "      Create a .env file with your API keys"
fi

echo ""

# Check if virtual environment exists
echo "2️⃣ Checking virtual environment..."
if [ -d "venv" ]; then
    echo "   ✅ Virtual environment found"
else
    echo "   ⚠️  Virtual environment not found"
    echo "      Run: python -m venv venv"
fi

echo ""

# Check Python version
echo "3️⃣ Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "   $python_version"

echo ""

# Check if dependencies are installed
echo "4️⃣ Checking dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
    if python -c "import crewai" 2>/dev/null; then
        echo "   ✅ Dependencies installed"
    else
        echo "   ⚠️  Dependencies not installed"
        echo "      Run: pip install -r requirements.txt"
    fi
    deactivate
fi

echo ""

# Check GitHub Actions
echo "5️⃣ GitHub Actions Setup:"
echo "   📋 Manual steps required:"
echo ""
echo "   a) Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions"
echo "   b) Look for 'Daily AI Briefer' workflow"
echo "   c) If disabled, click 'Enable workflow' button"
echo "   d) Click 'Run workflow' to test"
echo ""
echo "   🕐 Cron schedule: 8:00 AM UTC daily"
echo "      Your timezone:"
if command -v date &> /dev/null; then
    current_time=$(date)
    echo "      Current local time: $current_time"
fi

echo ""

# Check API quota
echo "6️⃣ API Quota Information:"
echo "   📊 Gemini 1.5 Flash: 1,500 requests/day (FREE)"
echo "   📊 Gemini 2.5 Flash: 20 requests/day (OLD - not recommended)"
echo ""
echo "   Check your usage:"
echo "   https://aistudio.google.com/app/apikey"

echo ""

# Solutions
echo "7️⃣ Common Solutions:"
echo ""
echo "   Problem: Cron not running"
echo "   Solution: Enable workflow in GitHub Actions tab"
echo "            GitHub disables workflows after 60 days of inactivity"
echo ""
echo "   Problem: 429 Rate Limit Error"
echo "   Solution: Upgrade to Gemini 1.5 Flash (done ✅)"
echo "            Or upgrade to paid tier"
echo "            Or wait 24 hours for quota reset"
echo ""
echo "   Problem: No Telegram messages"
echo "   Solution: Check GitHub Secrets are set correctly"
echo "            Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"

echo ""
echo "======================================="
echo "✅ Diagnostic complete!"
echo ""
echo "📖 For detailed troubleshooting, see: TROUBLESHOOTING.md"
echo ""
