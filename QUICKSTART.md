# 🚀 Serverless Setup - Quick Start

Follow these steps to deploy your AI Agent Briefer completely serverless in ~15 minutes.

## ✅ Checklist

### 1. GitHub Personal Access Token
- [ ] Go to https://github.com/settings/tokens
- [ ] Generate new token (classic)
- [ ] Select scopes: `repo` and `workflow`
- [ ] Copy token (starts with `ghp_`)

### 2. Add GitHub Secrets
- [ ] Go to your repo → Settings → Secrets → Actions
- [ ] Add all required secrets:
  - [ ] `GOOGLE_API_KEY`
  - [ ] `GROQ_API_KEY`
  - [ ] `OPENROUTER_API_KEY`
  - [ ] `MISTRAL_API_KEY`
  - [ ] `SERPER_API_KEY`
  - [ ] `ELEVENLABS_API_KEY`
  - [ ] `TELEGRAM_BOT_TOKEN`
  - [ ] `TELEGRAM_CHAT_ID`

### 3. Deploy to Vercel
- [ ] Sign up at https://vercel.com (free)
- [ ] Import your GitHub repository
- [ ] Click Deploy

### 4. Add Vercel Environment Variables
- [ ] Go to Vercel Dashboard → Your Project → Settings → Environment Variables
- [ ] Add these 4 variables:
  - [ ] `TELEGRAM_BOT_TOKEN` = your bot token
  - [ ] `TELEGRAM_CHAT_ID` = your chat ID
  - [ ] `GITHUB_TOKEN` = ghp_token from step 1
  - [ ] `GITHUB_REPO` = yourusername/ai-agent-briefer
- [ ] Redeploy the project

### 5. Set Telegram Webhook
- [ ] Get your Vercel URL: `https://your-project.vercel.app`
- [ ] Run the setup script:
  ```bash
  python setup_webhook.py
  ```
- [ ] Enter your webhook URL when prompted

### 6. Test It!
- [ ] Open Telegram
- [ ] Send `/help` to your bot
- [ ] Send `/brief` to trigger a briefing
- [ ] Check GitHub Actions tab to see it running

---

## 🎯 Quick Commands

### Set Webhook (Manual)
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
  -d "url=https://your-project.vercel.app/webhook"
```

### Check Webhook Status
```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
```

### Delete Webhook (if needed)
```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"
```

---

## 📋 What You Need

| Item | Where to Get It | Example |
|------|----------------|---------|
| GitHub Token | https://github.com/settings/tokens | `ghp_abc123...` |
| GitHub Repo | Your repository URL | `username/ai-agent-briefer` |
| Vercel URL | After Vercel deployment | `https://my-app.vercel.app` |
| Telegram Token | Already have from BotFather | `123456:ABC-DEF...` |
| Chat ID | Already have | `123456789` |

---

## 🔍 Verify Everything Works

1. **GitHub Actions scheduled run:**
   - Runs automatically at 6 AM IST daily
   - Check: Repository → Actions tab

2. **Telegram commands work:**
   - Send `/brief` in Telegram
   - Should see "🚀 Triggering daily tech brief..."
   - Check GitHub Actions for new workflow run

3. **Webhook is active:**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```
   Should show your Vercel URL

---

## 💰 Cost

Everything is **FREE**:
- ✅ GitHub Actions: 2,000 minutes/month
- ✅ Vercel: Unlimited requests, 100GB bandwidth
- ✅ Telegram: Free

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Webhook not responding | Check Vercel logs, verify environment variables |
| GitHub Actions not triggered | Verify GitHub token permissions |
| "Status 422" error | Check if branch is `main` not `master` |
| Bot not replying | Verify `TELEGRAM_CHAT_ID` matches your chat |

---

## 📖 Full Documentation

See [SERVERLESS_SETUP.md](SERVERLESS_SETUP.md) for complete details.

---

## ⚡ That's It!

Your bot is now running **100% serverless**:
- ✅ Daily briefings at 6 AM IST automatically
- ✅ On-demand briefings via Telegram commands
- ✅ No local hosting required
- ✅ Completely free!
