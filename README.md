# AI Agent Briefer

An AI-powered daily briefing agent that delivers tech news and interview preparation through Telegram.

## Features

- **Daily Tech Brief**: Get curated technology news with specific details, metrics, and announcements
- **Interview Prep**: Research companies and generate talking points for interviews
- **Telegram Bot**: Control everything from your Telegram chat
- **Voice Output**: Hear your briefings with ElevenLabs text-to-speech

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

4. Create a `.env` file with your API keys:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   SERPER_API_KEY=your_serper_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

### Getting API Keys

- **Google Gemini**: https://aistudio.google.com/app/apikey
- **Serper** (for web search): https://serper.dev/
- **ElevenLabs** (for voice): https://elevenlabs.io/
- **Telegram Bot**: Talk to [@BotFather](https://t.me/botfather) on Telegram
- **Telegram Chat ID**: Send a message to your bot, then visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` to find your chat_id

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

- ✅ Specific details with numbers, dates, and metrics
- ✅ Proper HTML formatting for Telegram
- ✅ Automatic retry on rate limits
- ✅ Voice output with ElevenLabs
- ✅ Real-time Telegram bot interface
- ✅ Multiple agent support (News Scout, Company Researcher)

## License

MIT
