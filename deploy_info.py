#!/usr/bin/env python3
"""
Quick deployment helper for serverless setup
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def print_header():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        AI Agent Briefer - Deployment Information              ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

def check_env_vars():
    """Check if required environment variables are set"""
    print("📋 Environment Variables Check")
    print("━" * 64)
    
    required_vercel = {
        "TELEGRAM_BOT_TOKEN": "Your Telegram bot token",
        "TELEGRAM_CHAT_ID": "Your Telegram chat ID",
        "GITHUB_TOKEN": "GitHub Personal Access Token",
        "GITHUB_REPO": "GitHub repository (username/repo)"
    }
    
    required_github = {
        "GOOGLE_API_KEY": "Google Gemini API key",
        "SERPER_API_KEY": "Serper search API key",
        "TELEGRAM_BOT_TOKEN": "Telegram bot token",
        "TELEGRAM_CHAT_ID": "Telegram chat ID"
    }
    
    print("\n✅ Vercel Environment Variables (add these to Vercel):")
    for key, desc in required_vercel.items():
        value = os.getenv(key)
        if value:
            masked = f"{value[:10]}..." if len(value) > 10 else value
            print(f"  ✓ {key} = {masked}")
        else:
            print(f"  ✗ {key} = NOT SET ({desc})")
    
    print("\n✅ GitHub Secrets (add these to GitHub repo):")
    for key, desc in required_github.items():
        value = os.getenv(key)
        if value:
            masked = f"{value[:10]}..." if len(value) > 10 else value
            print(f"  ✓ {key} = {masked}")
        else:
            print(f"  ✗ {key} = NOT SET ({desc})")

def show_deployment_commands():
    """Show deployment commands"""
    print("\n📦 Deployment Commands")
    print("━" * 64)
    print()
    print("1. Deploy to Vercel:")
    print("   npx vercel --prod")
    print()
    print("2. Or use Vercel Dashboard:")
    print("   https://vercel.com/new")
    print("   → Import your GitHub repository")
    print()

def show_webhook_setup():
    """Show webhook setup instructions"""
    print("\n🔗 Telegram Webhook Setup")
    print("━" * 64)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if bot_token:
        print()
        print("After deploying to Vercel, run:")
        print()
        print("  python setup_webhook.py")
        print()
        print("Or manually set webhook:")
        print()
        print(f'  curl -X POST "https://api.telegram.org/bot{bot_token}/setWebhook" \\')
        print('    -d "url=https://YOUR-PROJECT.vercel.app/webhook"')
        print()
        print("Check webhook status:")
        print()
        print(f'  curl "https://api.telegram.org/bot{bot_token}/getWebhookInfo"')
    else:
        print("\n  ⚠️  TELEGRAM_BOT_TOKEN not set in .env")

def show_next_steps():
    """Show next steps"""
    print("\n🚀 Next Steps")
    print("━" * 64)
    print()
    print("1. ✓ Create GitHub Personal Access Token")
    print("     https://github.com/settings/tokens")
    print("     Scopes: repo, workflow")
    print()
    print("2. ✓ Add secrets to GitHub repository")
    print("     Settings → Secrets and variables → Actions")
    print()
    print("3. ✓ Deploy to Vercel")
    print("     npx vercel --prod")
    print()
    print("4. ✓ Add environment variables to Vercel")
    print("     Dashboard → Settings → Environment Variables")
    print()
    print("5. ✓ Set Telegram webhook")
    print("     python setup_webhook.py")
    print()
    print("6. ✓ Test with /brief in Telegram")
    print()
    print("📖 See QUICKSTART.md for detailed instructions")

def main():
    print_header()
    check_env_vars()
    show_deployment_commands()
    show_webhook_setup()
    show_next_steps()
    print()
    print("━" * 64)
    print()

if __name__ == "__main__":
    main()
