# AI Agent Briefer

> AI-powered daily tech briefings and interview intelligence — delivered to Telegram with voice output. 100% free-tier, zero cost.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Serverless Deployment](#serverless-deployment-recommended)
  - [Local Development](#local-development)
- [Usage](#usage)
  - [Telegram Commands](#telegram-commands)
  - [CLI Commands](#cli-commands)
  - [Interview Edge — What You Get](#interview-edge--what-you-get)
- [Configuration](#configuration)
  - [API Keys](#api-keys)
  - [Environment Variables](#environment-variables)
  - [Model Selection](#model-selection)
  - [Audio Settings](#audio-settings)
- [Testing](#testing)
- [How It Works](#how-it-works)
  - [Output Validation](#output-validation)
  - [Multi-Model Fallback](#multi-model-fallback)
  - [Daily Schedule](#daily-schedule)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| **Daily Tech Brief** | 7–10 curated stories across AI/ML, cybersecurity, startups, cloud, and Indian tech — with specific details, metrics, and dates |
| **Interview Edge** | Deep company research: tech stack, recent moves, culture, challenges, killer questions, and a tactical interview playbook |
| **Voice Output** | ElevenLabs TTS with gTTS fallback — hear your briefings as Telegram audio messages |
| **Telegram Bot** | `/brief` for news, `/interview <company>` for interview prep |
| **Smart Validation** | Catches raw tool calls, template parroting, lazy agents, unfilled placeholders — auto-retries with the next model |
| **Multi-Model Fallback** | Automatic failover: Ollama → Groq → Gemini → OpenRouter → Mistral → Together AI → HuggingFace |
| **Serverless** | Deploy via Vercel + GitHub Actions — runs entirely in the cloud for free |

---

## Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌──────────────┐
│  Telegram Bot   │◄────►│   main.py    │◄────►│  agents.py   │
│  (User input)   │      │  (Orchestr.) │      │  (CrewAI)    │
└─────────────────┘      └──────┬───────┘      └──────┬───────┘
                                │                      │
                    ┌───────────┼───────────┐          │
                    ▼           ▼           ▼          ▼
              ┌──────────┐ ┌────────┐ ┌──────────┐ ┌────────┐
              │ Serper   │ │ LLM    │ │ Eleven-  │ │ gTTS   │
              │ (Search) │ │ APIs   │ │ Labs TTS │ │ (Free) │
              └──────────┘ └────────┘ └──────────┘ └────────┘
```

**Tech Stack:** Python · CrewAI · LiteLLM · Serper · ElevenLabs/gTTS · Telegram Bot API · Vercel · GitHub Actions

---

## Quick Start

### Serverless Deployment (Recommended)

No local hosting required — everything runs in the cloud.

| Component | What It Does |
|-----------|-------------|
| GitHub Actions | Runs the daily brief on a cron schedule + on-demand triggers |
| Vercel Webhook | Handles Telegram `/brief` and `/interview` commands |
| Free-tier APIs | All LLM, search, and TTS services at $0/month |

**Get started in 15 minutes:**
1. Follow [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions
2. Or see [SERVERLESS_SETUP.md](SERVERLESS_SETUP.md) for detailed documentation

### Local Development

1. **Clone and set up the environment:**

   ```bash
   git clone <repo-url> && cd ai-agent-briefer
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API keys** — create a `.env` file (see [Environment Variables](#environment-variables) below).

3. **Verify your setup:**

   ```bash
   python test_apis.py
   ```

4. **Run:**

   ```bash
   python main.py                      # Daily brief
   python main.py interview "Google"   # Interview prep
   python main.py bot                  # Telegram bot mode
   ```

---

## Usage

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/brief` | Get today's curated tech news briefing |
| `/interview <company>` | Deep interview intelligence for a specific company |
| `/help` | Show available commands |

### CLI Commands

```bash
python main.py                       # Run daily tech brief
python main.py interview "Google"    # Interview prep for a company
python main.py bot                   # Start Telegram bot (long-running)
```

### Interview Edge — What You Get

The `/interview` command runs 4 targeted searches and produces a complete intelligence briefing:

| Section | Details |
|---------|---------|
| **Company Intel** | What they do, HQ, CEO/CTO, employee count |
| **Tech Stack** | Languages, frameworks, databases, cloud services, CI/CD |
| **Recent News** | 3–5 events from the last 12 months with dates and numbers |
| **Culture & Team** | Work style (remote/hybrid/onsite), Glassdoor rating, review themes |
| **Challenges** | Competitors, business problems, technical pain points |
| **Killer Questions** | 5–7 questions that reference specific company facts |
| **Interview Playbook** | How to answer "Why this company?", when to drop facts, how to close strong |

Each briefing also generates a **voice summary** sent as a Telegram audio message.

---

## Configuration

### API Keys

All services used have a free tier — no credit card required.

#### Required: LLM (at least one)

| Provider | Free Tier | Get Key |
|----------|-----------|---------|
| **Groq** ⭐ | Unlimited | [console.groq.com/keys](https://console.groq.com/keys) |
| **Google Gemini** | 15 req/min | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| **Together AI** | $25 credits | [together.ai](https://together.ai) |
| **HuggingFace** | 1,000 req/day | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| **OpenRouter** | Limited | [openrouter.ai/keys](https://openrouter.ai/keys) |
| **Mistral** | Limited | [console.mistral.ai/api-keys](https://console.mistral.ai/api-keys) |

#### Required: Other Services

| Service | Free Tier | Get Key |
|---------|-----------|---------|
| **Serper** (web search) | 2,500 searches/month | [serper.dev](https://serper.dev/) |
| **Telegram Bot** | Unlimited | Talk to [@BotFather](https://t.me/botfather) |

#### Optional

| Service | Free Tier | Get Key |
|---------|-----------|---------|
| **ElevenLabs** (voice) | 10k chars/month | [elevenlabs.io](https://elevenlabs.io/) |

> **Tip:** Configure 2–3 LLM providers for automatic failover. The bot auto-switches if one hits rate limits.

### Environment Variables

Create a `.env` file in the project root:

```env
# ── LLM API Keys (at least one required) ──────────────────────
GROQ_API_KEY=your_key_here              # ⭐ Recommended
GOOGLE_API_KEY=your_key_here
TOGETHER_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here

# ── Search ─────────────────────────────────────────────────────
SERPER_API_KEY=your_key_here

# ── Telegram ───────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# ── Optional: Voice ───────────────────────────────────────────
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM   # Default: Rachel
ELEVENLABS_VOICE_NAME=Rachel

# ── Optional: Model Preferences ───────────────────────────────
PREFERRED_MODEL=groq                  # groq | gemini | together | huggingface | openrouter | mistral
GOOGLE_MODEL=gemini-2.0-flash        # Override Gemini model version

# ── Optional: Ollama (self-hosted) ────────────────────────────
OLLAMA_API_URL=https://your-ollama-instance/api/chat
OLLAMA_API_KEY=your_key_here
OLLAMA_MODEL=gpt-oss:120b-cloud
```

### Model Selection

The app tries models in a fallback chain. Set `PREFERRED_MODEL` to control the primary choice.

| Priority | Provider | Model | Free Tier |
|----------|----------|-------|-----------|
| 0 | **Ollama** | Configurable | Unlimited (self-hosted) |
| 1 | **Groq** ⭐ | Llama 3.3 70B Versatile | Unlimited |
| 2 | **Gemini** | 2.0 Flash | 15 req/min |
| 3 | **Together AI** | Llama 3.1 8B Turbo | $25 credits |
| 4 | **HuggingFace** | Llama 3 8B Instruct | 1,000 req/day |
| 5 | **OpenRouter** | Llama 3.1 8B (free) | Limited |
| 6 | **Mistral** | Small Latest | Limited |

> Ollama is tried first when configured. The remaining order follows `PREFERRED_MODEL`, then the default fallback sequence.

### Audio Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIO_USE_SUMMARY` | `true` | Summarise text before TTS (`true`) or read full output (`false`) |
| `AUDIO_SUMMARY_ITEMS` | `4` | Number of headline items in the audio summary |
| `AUDIO_MAX_CHARS` | `10000` | Maximum characters sent to TTS |

**ElevenLabs voices** (set via `ELEVENLABS_VOICE_ID`):

| Voice | Gender | ID |
|-------|--------|-----|
| Rachel | Female | `21m00Tcm4TlvDq8ikWAM` |
| Bella | Female | `EXAVITQu4vr4xnSDxMaL` |
| Elli | Female | `MF3mGyEYCl7XYWbV9V6O` |
| Adam | Male | `pNInz6obpgDQGcFmaJgB` |
| Antoni | Male | `ErXwobaYiN019PkySvjV` |
| Arnold | Male | `VR6AewLTigWG4xSOukaG` |

If ElevenLabs is unavailable, the system automatically falls back to **gTTS** (Google Text-to-Speech).

---

## Testing

```bash
# Quick — verify LLM API keys only
python test_llm_apis.py

# Full — test LLMs, Telegram, Serper, and all integrations
python test_apis.py
```

---

## How It Works

### Output Validation

Every LLM output is validated before delivery:

| Check | What It Catches |
|-------|----------------|
| **Raw tool calls** | LLM outputs search syntax instead of results |
| **Template parroting** | LLM copies instructions back verbatim |
| **Lazy agents** | 4+ sections say "Not found" (agent skipped searches) |
| **Unfilled placeholders** | Bracket placeholders like `[year]`, `[Name]` left in output |
| **Minimum length** | Output too short to be useful |
| **Topic diversity** | All stories are product launches (news brief only) |
| **Geographic coverage** | Missing global or Indian tech coverage (news brief only) |

Failed validation triggers an **automatic retry with the next model** in the fallback chain.

### Multi-Model Fallback

```
Ollama → Groq → Gemini → Together AI → HuggingFace → OpenRouter → Mistral
  │        │        │         │             │             │            │
  ▼        ▼        ▼         ▼             ▼             ▼            ▼
 fail?   fail?    fail?     fail?         fail?         fail?       fail?
  │        │        │         │             │             │            │
  └──next──┘──next──┘──next───┘───next──────┘────next─────┘───next────┘
```

- Rate-limit errors (429) trigger wait-and-retry with exponential backoff before moving to the next model
- Up to 5 model attempts per execution
- Error notifications sent to Telegram only after **all** models have been exhausted

### Daily Schedule

| Event | Time | Platform |
|-------|------|----------|
| Automated daily brief | 6:00 AM IST (8:00 AM UTC) | GitHub Actions |
| On-demand commands | Anytime | Telegram Bot / CLI |

> GitHub Actions may delay cron execution by 5–15 minutes during high load. Workflows auto-disable after 60 days of repo inactivity — re-enable from the Actions tab.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key errors | Run `python test_apis.py` to diagnose |
| Rate limits on all models | Wait for quota reset or add more API keys |
| No audio generated | Check `ELEVENLABS_API_KEY` or install `gTTS` as fallback |
| GitHub Actions not running | Re-enable workflow in the Actions tab (auto-disables after 60 days) |

For detailed guides:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues and solutions
- [MODEL_SWITCHING.md](MODEL_SWITCHING.md) — How to switch between AI models

---

## License

MIT
