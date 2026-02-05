#!/bin/bash

# Serverless Deployment Helper Script
# This script helps you verify your setup before deploying

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     AI Agent Briefer - Serverless Deployment Checker          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Load .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Found .env file"
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Checking Local Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check required variables for Vercel deployment
check_var() {
    if [ -z "${!1}" ]; then
        echo "❌ $1 is not set"
        return 1
    else
        # Mask the value for security
        masked="${!1:0:10}..."
        echo "✅ $1 is set ($masked)"
        return 0
    fi
}

all_good=true

# Vercel environment variables
check_var "TELEGRAM_BOT_TOKEN" || all_good=false
check_var "TELEGRAM_CHAT_ID" || all_good=false
check_var "GITHUB_TOKEN" || all_good=false
check_var "GITHUB_REPO" || all_good=false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  GitHub Actions Secrets (Add these to GitHub)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# These should be added to GitHub Secrets
check_var "GOOGLE_API_KEY" || echo "⚠️  Remember to add GOOGLE_API_KEY to GitHub Secrets"
check_var "GROQ_API_KEY" || echo "ℹ️  GROQ_API_KEY (optional)"
check_var "OPENROUTER_API_KEY" || echo "ℹ️  OPENROUTER_API_KEY (optional)"
check_var "MISTRAL_API_KEY" || echo "ℹ️  MISTRAL_API_KEY (optional)"
check_var "SERPER_API_KEY" || echo "⚠️  Remember to add SERPER_API_KEY to GitHub Secrets"
check_var "ELEVENLABS_API_KEY" || echo "ℹ️  ELEVENLABS_API_KEY (optional)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Git Repository Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in a git repository
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✅ Git repository found"
    
    # Get current branch
    branch=$(git branch --show-current)
    echo "ℹ️  Current branch: $branch"
    
    # Check if there are uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  You have uncommitted changes"
        echo "   Run: git add . && git commit -m 'Deploy' && git push"
    else
        echo "✅ No uncommitted changes"
    fi
    
    # Check remote
    remote=$(git config --get remote.origin.url)
    if [ -n "$remote" ]; then
        echo "✅ Remote repository: $remote"
    else
        echo "❌ No remote repository configured"
        all_good=false
    fi
else
    echo "❌ Not a git repository. Run: git init"
    all_good=false
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Required Files Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1 exists"
    else
        echo "❌ $1 is missing"
        all_good=false
    fi
}

check_file "api/webhook.py"
check_file "vercel.json"
check_file ".github/workflows/briefer.yml"
check_file "requirements.txt"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$all_good" = true ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "Ready to deploy! Follow these steps:"
    echo ""
    echo "1. Push to GitHub:"
    echo "   git add ."
    echo "   git commit -m 'Ready for serverless deployment'"
    echo "   git push"
    echo ""
    echo "2. Deploy to Vercel:"
    echo "   npx vercel --prod"
    echo "   (Or import from GitHub on vercel.com)"
    echo ""
    echo "3. Add Vercel environment variables:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
    echo "   - GITHUB_TOKEN"
    echo "   - GITHUB_REPO"
    echo ""
    echo "4. Set Telegram webhook:"
    echo "   python setup_webhook.py"
    echo ""
    echo "5. Test with /brief in Telegram!"
    echo ""
    echo "📖 See SERVERLESS_SETUP.md for detailed instructions"
else
    echo "❌ Some checks failed. Please fix the issues above."
    echo ""
    echo "📖 See SERVERLESS_SETUP.md for help"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
