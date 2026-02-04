# Troubleshooting Guide

## Quick Diagnostic Test

**Before troubleshooting, run the API test script:**

```bash
python test_apis.py
```

This will automatically test all your APIs and show exactly what's working and what's not. It tests:
- Environment variables
- Gemini 1.5 Flash API
- Gemini 2.5 Flash API
- Serper search API
- Telegram bot
- ElevenLabs (optional)
- Full CrewAI agent integration

The script will show you exactly which API is failing and why.

---

## Issue 1: Cron Job Not Running at 8 AM Daily

### Problem
GitHub Actions scheduled workflows (`cron` jobs) are not running automatically.

### Solutions

#### Solution A: Enable Workflow in GitHub (Required)
1. Go to your GitHub repository
2. Click on **Actions** tab
3. Look for "Daily AI Briefer" workflow in the left sidebar
4. If you see a banner saying "This workflow was disabled", click **Enable workflow**
5. GitHub automatically disables workflows after 60 days of repository inactivity

#### Solution B: Verify Workflow Permissions
1. Go to repository **Settings** → **Actions** → **General**
2. Under "Workflow permissions", ensure "Read and write permissions" is selected
3. Check "Allow GitHub Actions to create and approve pull requests" if needed

#### Solution C: Manual Trigger Test
1. Go to **Actions** tab
2. Click "Daily AI Briefer" workflow
3. Click "Run workflow" dropdown
4. Select "daily" mode and click "Run workflow"
5. This verifies the workflow works and resets the inactivity timer

### Important Notes
- The cron is set to `0 8 * * *` = **8:00 AM UTC** (not your local time)
- Convert to your timezone:
  - PST: 12:00 AM (midnight)
  - EST: 3:00 AM
  - IST: 1:30 PM
- GitHub Actions cron jobs can be delayed by 5-15 minutes during high load

---

## Issue 2: Gemini API Quota Exceeded (429 Error)

### Problem
```
429 RESOURCE_EXHAUSTED
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
limit: 20, model: gemini-2.5-flash
```

### Root Cause
The free tier of Gemini API only allows **20 requests per day**. Your CrewAI agents make multiple API calls per run (5-10+ requests).

### Solutions (Choose One)

#### Option A: Use Built-in Fallback (Easiest) ⭐ RECOMMENDED
The app automatically falls back to other free-tier providers if Gemini hits limits.

Add any of these to your `.env` file:
```env
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key
MISTRAL_API_KEY=your_mistral_key
```

The app will automatically try: Gemini → Groq → OpenRouter → Mistral

#### Option B: Switch to Gemini 1.5 Flash (Free Tier - 1500 req/day)
Already implemented! The code now uses Gemini 1.5 Flash with 1500 req/day limit.

**If you're using Gemini 2.5 Flash:** It only has 20 req/day. Switch to 1.5:
```env
# In .env, remove this line or change it:
PREFERRED_MODEL=gemini  # Uses 1.5 Flash (1500 req/day)
```

#### Option C: Manually Select a Model
Set your preferred model in `.env`:
```env
PREFERRED_MODEL=groq  # Options: gemini, gemini-2.5, groq, openrouter, mistral
GROQ_API_KEY=your_groq_key
```

#### Option D: Upgrade to Paid Gemini Tier
Get a Google Cloud billing account:
- Go to https://console.cloud.google.com/
- Enable billing for your project
- Gemini API pricing: ~$0.075 per 1M input tokens
- Daily brief cost: ~$0.01-0.05 per run

#### Option E: Use Alternative Free-Tier LLM
Switch to a different free-tier provider:

**Groq** (Fast & Free)
```env
PREFERRED_MODEL=groq
GROQ_API_KEY=your_groq_key
```
- Get key: https://console.groq.com/keys

**OpenRouter** (Free tier available)
```env
PREFERRED_MODEL=openrouter
OPENROUTER_API_KEY=your_openrouter_key
```
- Get key: https://openrouter.ai/keys

**Mistral** (Free tier available)
```env
PREFERRED_MODEL=mistral
MISTRAL_API_KEY=your_mistral_key
```
- Get key: https://console.mistral.ai/api-keys

---

## Model Comparison Table

| Model | Free Tier | Cost (Paid) | Speed | Quality | Best For |
|-------|-----------|-------------|-------|---------|----------|
| **Gemini 1.5 Flash** | 1500 req/day ✅ | $0.075/1M | Fast | Good | Daily use (default) |
| **Gemini 2.5 Flash** | 20 req/day \u26a0\ufe0f | $0.075/1M | Fastest | Better | One-off queries only |
| **Groq Llama 3.1 8B** | Free tier ✅ | Free | Very Fast | Good | Speed |
| **OpenRouter Mistral 7B** | Free tier ✅ | Free | Fast | Good | Variety |

| **Mistral Open 7B** | Free tier ✅ | Free | Fast | Good | Official API |

---

## How the Fallback Works

1. App tries **Gemini 1.5 Flash** first (if `GOOGLE_API_KEY` is set)
2. If Gemini fails, tries **Groq** (if `GROQ_API_KEY` is set)
3. If Groq fails, tries **OpenRouter** (if `OPENROUTER_API_KEY` is set)
4. If OpenRouter fails, tries **Mistral** (if `MISTRAL_API_KEY` is set)
5. If all fail, shows error message

**Override the order:**
```env
PREFERRED_MODEL=groq  # Start with Groq instead
```

---

## Implementing the Fixes

### Fix 1: Update to Gemini 1.5 Flash
The updated `agents.py` now uses `gemini-1.5-flash` with 1500 req/day limit.

### Fix 2: Better Retry Logic
Updated `main.py` with:
- Exponential backoff (60s → 120s → 240s)
- Max 2 retries to avoid infinite loops
- Better error messages

### Fix 3: Rate Limit Prevention
Added delays between operations to stay under quota.

---

## Monitoring Your Usage

### Check Gemini API Usage
1. Visit: https://aistudio.google.com/app/apikey
2. Click on your API key
3. View usage statistics and quota

### Check GitHub Actions Usage
1. Go to repository **Settings** → **Actions**
2. View minutes used (2,000 free minutes/month)

---

## Quick Checklist

- [ ] Enable workflow in GitHub Actions tab
- [ ] Verify GitHub secrets are set correctly:
  - `GOOGLE_API_KEY`
  - `SERPER_API_KEY`
  - `ELEVENLABS_API_KEY`
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
- [ ] Updated to Gemini 1.5 Flash (`agents.py`)
- [ ] Understand the cron runs at 8 AM UTC, not local time
- [ ] Don't manually trigger too many times (quota limit)
- [ ] Consider upgrading to paid tier if using daily

---

## Testing

### Test Locally
```bash
# Activate virtual environment
source venv/bin/activate

# Test daily brief (uses your quota!)
python main.py

# Test interview prep
python main.py interview "Google"
```

### Test GitHub Actions
1. Go to **Actions** tab
2. Run workflow manually
3. Check logs for errors
4. Verify Telegram message received
