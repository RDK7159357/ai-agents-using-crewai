# Model Switching Guide (Free-Tier Providers)

## Quick Start: Switch Models in 30 Seconds

### Switch to Gemini 2.5 Flash (Newest, Limited Quota)
```bash
# Already have GOOGLE_API_KEY? Just change preference:
echo "PREFERRED_MODEL=gemini-2.5" >> .env

# Run the bot
python main.py

# ⚠️ Only 20 requests/day on free tier
```

### Switch to Groq (Fast)
```bash
# Get key: https://console.groq.com/keys
echo "GROQ_API_KEY=your-groq-key" >> .env
echo "PREFERRED_MODEL=groq" >> .env

python main.py
```

### Switch to OpenRouter (Mistral 7B)
```bash
# Get key: https://openrouter.ai/keys
echo "OPENROUTER_API_KEY=your-openrouter-key" >> .env
echo "PREFERRED_MODEL=openrouter" >> .env

python main.py
```

### Switch to Mistral (Open Mistral 7B)
```bash
# Get key: https://console.mistral.ai/api-keys
echo "MISTRAL_API_KEY=your-mistral-key" >> .env
echo "PREFERRED_MODEL=mistral" >> .env

python main.py
```

### Use Automatic Fallback (Recommended)
```bash
# Add multiple API keys - app will fallback automatically
echo "GOOGLE_API_KEY=your-gemini-key" >> .env
echo "GROQ_API_KEY=your-groq-key" >> .env
echo "OPENROUTER_API_KEY=your-openrouter-key" >> .env
echo "MISTRAL_API_KEY=your-mistral-key" >> .env

# No PREFERRED_MODEL needed - defaults to Gemini → Groq → OpenRouter → Mistral
```

---

## Model Comparison (Free Tier)

| Feature | Gemini 1.5 Flash | Gemini 2.5 Flash | Groq Llama 3.1 8B | OpenRouter Mistral 7B | Mistral Open 7B |
|---------|------------------|------------------|-------------------|------------------------|------------------|
| **Free Tier** | ✅ 1500 req/day | ⚠️ 20 req/day | ✅ Available | ✅ Available | ✅ Available |
| **Speed** | Fast | Fastest | Very Fast | Fast | Fast |
| **Quality** | Good | Better | Good | Good | Good |
| **Best For** | Daily automation | Testing, one-off | Speed | Variety | Official API |
| **Recommended** | ✅ Default | ❌ Not for cron | ✅ Yes | ✅ Yes | ✅ Yes |

---

## GitHub Actions Setup

Add these secrets to your GitHub repository:

### For Gemini (Default)
```
Name: GOOGLE_API_KEY
Value: your-gemini-api-key
```

### Optional Free-Tier Fallbacks
```
Name: GROQ_API_KEY
Value: your-groq-key

Name: OPENROUTER_API_KEY
Value: your-openrouter-key

Name: MISTRAL_API_KEY
Value: your-mistral-key

Name: PREFERRED_MODEL (optional)
Value: groq | openrouter | mistral | gemini | gemini-2.5
```

---

## Troubleshooting

### "No LLM API keys found"
**Problem:** No API key is set in `.env` or GitHub Secrets

**Solution:** Add at least one:
```bash
# Option 1: Gemini (Free)
GOOGLE_API_KEY=your-key

# Option 2: Groq (Free)
GROQ_API_KEY=your-key

# Option 3: OpenRouter (Free)
OPENROUTER_API_KEY=your-key

# Option 4: Mistral (Free)
MISTRAL_API_KEY=your-key
```

### Rate Limit with Gemini
**Problem:** Hit 1500 requests/day limit (Gemini 1.5) or 20 requests/day (Gemini 2.5)

**Solutions:**
1. **If using Gemini 2.5**: Switch to Gemini 1.5 Flash for 75x more quota
2. Wait 24 hours (free)
3. Add Groq/OpenRouter/Mistral as fallbacks
4. Use `PREFERRED_MODEL=groq` (or another free-tier provider)

---

## Recommendations

### For Daily Automation
✅ **Gemini 1.5 Flash** (default)
- 1,500 requests/day is enough for daily briefs

### For Speed
✅ **Groq** (Llama 3.1 8B Instant)
- Extremely fast inference

### For Variety
✅ **OpenRouter**
- Access to multiple open models

### For Official Mistral API
✅ **Mistral**
- Direct Mistral endpoint

---

## Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verify API keys are valid at the provider dashboard
3. Run `python test_llm_apis.py` to verify keys
