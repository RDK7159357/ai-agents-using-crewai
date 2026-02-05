# Complete Serverless Setup Guide

This guide sets up your AI Agent Briefer to run **100% serverless** with no local hosting required.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Telegram   │─────>│    Vercel    │─────>│ GitHub Actions  │
│    User     │      │   Webhook    │      │   Workflows     │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │                        │
                            └────────────────────────┘
                                  Sends results
                                  to Telegram
```

**Components:**
1. **Telegram Bot** - User interface (commands)
2. **Vercel Webhook** - Serverless function to receive Telegram updates
3. **GitHub Actions** - Runs your Python scripts in the cloud
4. **Scheduled Cron** - Runs daily at 6 AM IST automatically

## Prerequisites

- GitHub account (free)
- Vercel account (free) - Sign up at https://vercel.com
- Telegram bot token (you already have this)
- GitHub Personal Access Token

---

## Part 1: GitHub Setup

### Step 1: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Settings:
   - **Note:** "Telegram Bot Workflow Trigger"
   - **Expiration:** 90 days or No expiration
   - **Scopes:** Check these boxes:
     - ✅ `repo` (Full control of repositories)
     - ✅ `workflow` (Update GitHub Actions)
4. Click **"Generate token"**
5. **Copy the token** (starts with `ghp_`) - you won't see it again!

### Step 2: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each of these:

```
GOOGLE_API_KEY          = your_google_api_key
GROQ_API_KEY            = your_groq_api_key
OPENROUTER_API_KEY      = your_openrouter_api_key
MISTRAL_API_KEY         = your_mistral_api_key
SERPER_API_KEY          = your_serper_api_key
ELEVENLABS_API_KEY      = your_elevenlabs_api_key
TELEGRAM_BOT_TOKEN      = your_telegram_bot_token
TELEGRAM_CHAT_ID        = your_telegram_chat_id
PREFERRED_MODEL         = gemini-2.0-flash-exp (optional)
```

### Step 3: Verify Workflow File

Your workflow at `.github/workflows/briefer.yml` should be committed to your repository.

✅ **Already configured to run at 6 AM IST daily!**

---

## Part 2: Vercel Deployment

### Step 1: Install Vercel CLI (Optional but Recommended)

```bash
npm install -g vercel
```

Or deploy via Vercel Dashboard (easier).

### Step 2: Deploy to Vercel

#### Option A: Using Vercel Dashboard (Easiest)

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your GitHub repository
4. Vercel will auto-detect the project
5. Click **"Deploy"**

#### Option B: Using Vercel CLI

```bash
# Login to Vercel
vercel login

# Deploy from project directory
cd /Users/ramadugudhanush/Documents/ai-agent-briefer
vercel --prod
```

### Step 3: Add Environment Variables in Vercel

After deployment:

1. Go to your project in Vercel Dashboard
2. Click **Settings** → **Environment Variables**
3. Add these variables:

```
TELEGRAM_BOT_TOKEN      = your_telegram_bot_token
TELEGRAM_CHAT_ID        = your_telegram_chat_id
GITHUB_TOKEN            = ghp_your_github_token_from_step1
GITHUB_REPO             = yourusername/ai-agent-briefer
```

**Important:** Replace `yourusername/ai-agent-briefer` with your actual GitHub username and repo name.

4. Click **"Save"**
5. **Redeploy** the project for changes to take effect

### Step 4: Get Your Webhook URL

After deployment, you'll get a URL like:
```
https://your-project-name.vercel.app
```

Your webhook endpoint will be:
```
https://your-project-name.vercel.app/webhook
```

**Copy this URL** - you'll need it for the next step.

---

## Part 3: Configure Telegram Webhook

### Set the Webhook

Replace the values and run this command in your terminal:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-project-name.vercel.app/webhook"}'
```

**Example:**
```bash
curl -X POST "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://my-briefer.vercel.app/webhook"}'
```

### Verify Webhook is Set

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

You should see:
```json
{
  "ok": true,
  "result": {
    "url": "https://your-project-name.vercel.app/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## Part 4: Testing

### Test Commands in Telegram

1. Open your Telegram bot
2. Send these commands:

```
/help               → Shows help message
/brief              → Triggers daily briefing
/interview Google   → Triggers interview prep
```

### Monitor Execution

**GitHub Actions:**
1. Go to your repository
2. Click **Actions** tab
3. You'll see workflows running

**Vercel Logs:**
1. Go to Vercel Dashboard
2. Select your project
3. Click **Deployments** → Click on latest deployment
4. View **Runtime Logs**

---

## How It Works

### Daily Scheduled Brief (Automatic)

```
6:00 AM IST Daily
      ↓
GitHub Actions Cron
      ↓
Runs main.py
      ↓
Sends to Telegram
```

### On-Demand Commands (Manual)

```
You: /brief in Telegram
      ↓
Telegram → Vercel Webhook
      ↓
Vercel triggers GitHub Actions
      ↓
GitHub Actions runs main.py
      ↓
Results sent to Telegram
```

---

## Troubleshooting

### Webhook not responding

**Check webhook is set:**
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

**Delete and reset webhook:**
```bash
# Delete
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"

# Set again
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://your-project.vercel.app/webhook"
```

### GitHub Actions not triggering

1. Check `GITHUB_TOKEN` has correct permissions
2. Verify `GITHUB_REPO` format is `username/repo`
3. Check Vercel logs for error messages
4. Verify your default branch is `main` (not `master`)

### "Failed to trigger workflow. Status: 422"

Your default branch might not be `main`. Check with:
```bash
git branch --show-current
```

If it's `master`, update [api/webhook.py](api/webhook.py):
```python
"ref": "master",  # Change from "main"
```

Then redeploy to Vercel.

### Vercel deployment fails

Make sure `requirements.txt` includes:
```
requests
flask
python-dotenv
```

---

## Cost Analysis

| Service | Cost | Notes |
|---------|------|-------|
| GitHub Actions | **FREE** | 2,000 minutes/month on free tier |
| Vercel | **FREE** | 100 GB bandwidth, unlimited requests |
| Telegram Bot | **FREE** | No costs |
| **Total** | **$0/month** | ✅ Completely free! |

---

## Maintenance

### Update Code

1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update code"
   git push
   ```

2. Vercel auto-deploys on push (if connected to GitHub)
   - Or manually: `vercel --prod`

### Monitor Usage

- **GitHub Actions:** Settings → Billing → Usage
- **Vercel:** Dashboard → Usage

### Update Environment Variables

**Vercel:**
- Dashboard → Your Project → Settings → Environment Variables

**GitHub:**
- Repository → Settings → Secrets and variables → Actions

---

## Security Best Practices

1. ✅ Never commit `.env` file to Git
2. ✅ Rotate GitHub token every 90 days
3. ✅ Use environment variables for all secrets
4. ✅ Limit `TELEGRAM_CHAT_ID` to only your chat
5. ✅ Keep bot token private

---

## Quick Reference

### Your Configuration

```bash
# GitHub
Repo: yourusername/ai-agent-briefer
Token: ghp_xxxxx... (keep secret!)

# Vercel
URL: https://your-project.vercel.app
Webhook: https://your-project.vercel.app/webhook

# Telegram
Bot: @your_bot_name
Commands: /brief, /interview <company>, /help
```

### Useful Commands

```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Delete webhook
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"

# Deploy to Vercel
vercel --prod

# View Vercel logs
vercel logs
```

---

## What's Running Where?

| Component | Where it Runs | When |
|-----------|---------------|------|
| Telegram Bot | Telegram Servers | Always |
| Webhook Handler | Vercel (Serverless) | On command |
| Python Scripts | GitHub Actions | On schedule + on demand |
| Cron Schedule | GitHub Actions | Daily 6 AM IST |

**Result:** Nothing runs on your computer! Everything is in the cloud. 🎉

---

## Next Steps

1. ✅ Set up GitHub token and secrets
2. ✅ Deploy to Vercel
3. ✅ Set Telegram webhook
4. ✅ Test with `/brief` command
5. ✅ Wait for tomorrow's 6 AM brief!

Need help? Check the logs in:
- Vercel Dashboard → Runtime Logs
- GitHub → Actions tab → Workflow runs
