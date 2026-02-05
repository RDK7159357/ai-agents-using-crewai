# AI Agent Briefer

An AI-powered daily briefing agent that delivers tech news and interview preparation through Telegram.

## 🚀 Quick Start - Serverless Deployment

**Want to run this 100% serverless with no local hosting?**

See [QUICKSTART.md](QUICKSTART.md) for a 15-minute setup guide using Vercel + GitHub Actions (completely free!)

## Features

- **Daily Tech Brief**: Get curated technology news with specific details, metrics, and announcements
- **Interview Prep**: Research companies and generate talking points for interviews
- **Telegram Bot**: Control everything from your Telegram chat
- **Voice Output**: Hear your briefings with ElevenLabs text-to-speech
- **Serverless**: Deploy to Vercel for 100% cloud operation

## Setup

### ⚡ Serverless Setup (Recommended - No Local Hosting!)

Your bot is **100% serverless** - everything runs in the cloud!

**Daily Brief:** Runs automatically at 6:00 AM IST every day
**On-Demand:** Send `/brief` or `/interview <company>` in Telegram anytime (optional webhook setup)

**Quick Setup:**
1. See [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions (15 minutes)
2. Or read [SERVERLESS_SETUP.md](SERVERLESS_SETUP.md) for detailed documentation

**What's Deployed:**
- ✅ GitHub Actions Workflow - Runs daily + on-demand
- ✅ Vercel Serverless Webhook - Handles Telegram commands (optional)
- ✅ Free tier APIs - Everything costs $0/month

**That's it! No local setup needed.** 🎉

---

### Local Development (Optional)

If you want to run locally or test:

1. Clone the repository

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```env
   # Required - 100% FREE
   GOOGLE_API_KEY=your_gemini_api_key          # FREE: 1500 requests/day!
   SERPER_API_KEY=your_serper_api_key          # FREE tier available
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token  # FREE
   TELEGRAM_CHAT_ID=your_telegram_chat_id      # FREE
   
   # Optional - FREE
   ELEVENLABS_API_KEY=your_elevenlabs_api_key  # FREE: 10k chars/month
   GROQ_API_KEY=your_groq_api_key               # FREE tier available
   OPENROUTER_API_KEY=your_openrouter_api_key   # FREE tier available
   MISTRAL_API_KEY=your_mistral_api_key         # FREE tier available
   PREFERRED_MODEL=gemini                       # Options: gemini, gemini-2.5, groq, openrouter, mistral
   ```

5. Test your API keys:
   ```bash
   python test_apis.py
   ```

6. Run locally:
   ```bash
   # Daily Brief
   python main.py
   
   # Interview Prep
   python main.py interview "Google"
   ```
   
   **This app uses 100% FREE tier models - no paid APIs required!**

### Getting API Keys (All FREE!)

**Required (100% Free):**
- **Google Gemini**: https://aistudio.google.com/app/apikey - **FREE: 1,500 requests/day**
- **Serper** (for web search): https://serper.dev/ - FREE tier: 2,500 searches/month
- **Telegram Bot**: Talk to [@BotFather](https://t.me/botfather) on Telegram - FREE
- **Telegram Chat ID**: Send a message to your bot, then visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` to find your chat_id - FREE

**Optional (Free tier available):**
- **ElevenLabs** (for voice): https://elevenlabs.io/ - FREE tier: 10k characters/month
- **Groq**: https://console.groq.com/keys - FREE tier available
- **OpenRouter**: https://openrouter.ai/keys - FREE tier available
- **Mistral**: https://console.mistral.ai/api-keys - FREE tier available

**💰 This entire setup costs $0 - everything runs on free tiers!**

## Testing Your Setup

Before running the bot, test your LLM API keys:

```bash
# Test just the LLM APIs (Gemini, Groq, OpenRouter, Mistral)
python test_llm_apis.py

# Or test everything (including Telegram, Serper, etc.)
python test_apis.py
```

**Recommended:** Start with `test_llm_apis.py` to quickly verify your AI model keys.

This will test:
- ✅ Gemini 1.5 Flash API (1500 req/day FREE)
- ✅ Gemini 2.5 Flash API (20 req/day FREE)
- ✅ Groq (optional, free tier)
- ✅ OpenRouter (optional, free tier)
- ✅ Mistral AI (optional, free tier)

**Sample output:**
```
╔═══════════════════════════════════════════════════════════════════╗
║              LLM API TESTING SCRIPT                               ║
║     Test Gemini, Groq, OpenRouter, Mistral Keys                  ║
╚═══════════════════════════════════════════════════════════════════╝

====================================================================
              Testing Gemini 1.5 Flash API
====================================================================

ℹ️  API Key: AIzaSyC1D2...E3F4
ℹ️  Initializing Gemini 1.5 Flash...
ℹ️  Sending test prompt: 'Say hello'
✅ ✓ Response received in 1.23 seconds
✅ Gemini 1.5 Flash API is working!
ℹ️  Free tier: 1,500 requests/day ✨

====================================================================
                          Summary
====================================================================

Free Tier Models:
✅ Gemini 1.5 Flash: Working ✓ (1,500 req/day FREE)

Additional Free Tier Providers (Optional):
ℹ️  Groq: Not configured (optional)
ℹ️  OpenRouter: Not configured (optional)
ℹ️  Mistral: Not configured (optional)

✨ You're all set! Gemini 1.5 Flash is working.
```

## Usage

### Telegram Commands

Send these commands to your bot:

```
/brief              - Get today's tech news briefing
/interview Google   - Get interview prep for a company
/help              - Show help message
```

### Daily Schedule

The bot automatically sends you a tech brief every day at **6:00 AM IST**.

No action needed - it just works! 🤖

## Features

- ✅ **100% FREE** - No paid APIs required, runs entirely on free tiers
- ✅ Specific details with numbers, dates, and metrics
- ✅ Proper HTML formatting for Telegram
- ✅ **Gemini 1.5 Flash**: 1,500 free requests/day (default)
- ✅ **Gemini 2.5 Flash**: 20 free requests/day (experimental, newest model)
- ✅ Smart rate limiting and retry logic
- ✅ Voice output with ElevenLabs (free tier)
- ✅ Real-time Telegram bot interface
- ✅ Multiple agent support (News Scout, Company Researcher)
- ✅ Automated daily briefings at 8 AM UTC via GitHub Actions (free)

## Important Notes

### Model Selection (100% Free)
This app uses only FREE tier AI models - no costs!

1. **Gemini 1.5 Flash** (Default) ⭐
   - ✅ **1,500 free requests/day**
   - ✅ Fast and capable
   - ✅ Perfect for daily automation
   - ✅ Default model - no config needed

2. **Gemini 2.5 Flash** (Experimental)
   - ⚠️ **Only 20 free requests/day**
   - ✅ Newest model, improved quality
   - ⚠️ Limited quota - not for automation
   - Use: Set `PREFERRED_MODEL=gemini-2.5`

3. **Groq** (Llama 3.1 8B Instant)
   - ✅ Free tier available
   - ✅ Very fast inference
   - Use: Set `PREFERRED_MODEL=groq`

4. **OpenRouter** (Mistral 7B Instruct)
   - ✅ Free tier available
   - ✅ Access to multiple open models
   - Use: Set `PREFERRED_MODEL=openrouter`

5. **Mistral** (Open Mistral 7B)
   - ✅ Free tier available
   - ✅ Official Mistral API
   - Use: Set `PREFERRED_MODEL=mistral`

**All models above are free-tier eligible - no credit card needed!**

### API Quotas (All FREE) (All FREE)
- **Gemini 1.5 Flash**: 1,500 requests/day ✅ (default)
- **Gemini 2.5 Flash**: 20 requests/day ⚠️ (experimental)
- **Groq**: Free tier available ✅
- **OpenRouter**: Free tier available ✅
- **Mistral**: Free tier available ✅
- **Serper**: 2,500 searches/month ✅
- **ElevenLabs**: 10k characters/month ✅ (optional)
- Each brief uses ~5-15 Gemini requests
- **Daily cost: $0** 🎉

### GitHub Actions Cron
- Runs at **8:00 AM UTC** (not local time)
- GitHub may delay execution by 5-15 minutes during high load
- Workflows auto-disable after 60 days of repo inactivity - re-enable in Actions tab
- **First-time setup**: Enable workflow in GitHub Actions tab

### Troubleshooting
If you encounter issues, see:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [MODEL_SWITCHING.md](MODEL_SWITCHING.md) - How to switch between AI models

## License

MIT
