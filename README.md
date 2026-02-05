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

4. Test your API keys:
   ```bash
   python test_apis.py
   ```
   
   This will verify all your API keys are working correctly before you start!

5. Create a `.env` file with your API keys:
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

### Option 1: Fully Serverless (Recommended - No local running needed!)

Deploy the webhook to Vercel and use Telegram webhooks instead of polling.

**Setup:**

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Push your code to GitHub

3. Deploy to Vercel:
   ```bash
   vercel
   ```

4. Add environment variables in Vercel dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GITHUB_TOKEN`
   - `GITHUB_REPO` (format: username/repo-name)

5. Add GitHub secrets (Settings → Secrets and variables → Actions):
   - `GOOGLE_API_KEY`
   - `SERPER_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

6. Set up Telegram webhook (run once):
   ```bash
   python3.12 setup_webhook.py
   # Enter your Vercel URL: https://your-app.vercel.app/webhook
   ```

7. Done! Now just send commands in Telegram:
   ```
   /brief
   /interview Google
   ```

Everything runs serverless - Vercel handles Telegram webhooks, GitHub Actions runs the agents!

### Option 2: GitHub Actions with Local Bot

This approach runs the agents on GitHub's infrastructure, so you don't need a server running 24/7.

**Setup:**

1. Push your code to GitHub
2. Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):
   - `GOOGLE_API_KEY`
   - `SERPER_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

3. Add these to your `.env` file locally:
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_REPO=username/repo-name
   ```

4. Create a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select `repo` scope (full control of private repositories)
   - Copy the token to your `.env` file

5. Run the Telegram bot locally:
   ```bash
   python3.12 telegram_bot_github.py
   ```

6. Send commands in Telegram:
   ```
   /brief
   /interview Google
   ```

The bot will trigger GitHub Actions workflows that run the agents in the cloud and send results to your Telegram!

### Option 2: Command Line (Local)

**Daily Brief:**
```bash
python3.12 main.py
```

**Interview Prep:**
```bash
python3.12 main.py interview "Google"
```

### Option 3: Telegram Bot (Local)

**Start the bot:**
```bash
python3.12 main.py bot
```

**Available Commands:**
- `/brief` - Get today's tech news briefing
- `/interview <company>` - Get interview prep for a company
- `/help` - Show help message

**Examples:**
```
/brief
/interview Google
/interview OpenAI
```

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
