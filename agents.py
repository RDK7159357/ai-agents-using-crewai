from dotenv import load_dotenv
import os
import re
import time
from datetime import datetime
from crewai import Agent, LLM
from crewai_tools import SerperDevTool

load_dotenv()

# Track which models have already been tried to avoid infinite loops
_models_tried = set()

def reset_tried_models():
    """Reset the list of tried models for retry logic"""
    global _models_tried
    _models_tried = set()

def get_llm(skip_models=None, prefer_model=None):
    """
    Get LLM with fallback support.
    Tries models in order based on PREFERRED_MODEL setting.
    Set PREFERRED_MODEL in .env to override (gemini, groq, openrouter, mistral)
    
    Args:
        skip_models: Set of model names to skip (used for fallback retries)
        prefer_model: Override PREFERRED_MODEL for this call (e.g., "gemini" for high-context tasks)
    """
    if skip_models is None:
        skip_models = set()
    
    # Use override if provided, otherwise use env variable
    preferred_model = (prefer_model or os.getenv("PREFERRED_MODEL", "groq")).lower()
    
    models_config = {
        "groq": {
            "model": "llama-3.3-70b-versatile",
            "api_key_env": "GROQ_API_KEY",
            "name": "Groq Llama 3.3 70B Versatile",
            "free_tier": "unlimited ⭐"
        },
        "gemini": {
            "model": os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
            "api_key_env": "GOOGLE_API_KEY",
            "name": "Gemini 2.0 Flash",
            "free_tier": "15 req/min"
        },
        "together": {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "api_key_env": "TOGETHER_API_KEY",
            "name": "Together AI Llama 3.1 8B",
            "free_tier": "$25 free credits"
        },
        "huggingface": {
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "api_key_env": "HUGGINGFACE_API_KEY",
            "name": "Hugging Face Llama 3 8B",
            "free_tier": "1000 req/day"
        },
        "openrouter": {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "api_key_env": "OPENROUTER_API_KEY",
            "name": "OpenRouter Llama 3.1 8B (free)",
            "free_tier": "limited"
        },
        "mistral": {
            "model": "mistral-small-latest",
            "api_key_env": "MISTRAL_API_KEY",
            "name": "Mistral Small Latest",
            "free_tier": "limited"
        }
    }
    
    # Default fallback order
    fallback_order = ["groq", "together", "huggingface", "gemini", "openrouter", "mistral"]
    
    # Move preferred model to front if specified
    if preferred_model in models_config:
        if preferred_model in fallback_order:
            fallback_order.remove(preferred_model)
        fallback_order.insert(0, preferred_model)
    
    # Try each model in order (skip already-tried ones)
    for model_name in fallback_order:
        if model_name in skip_models:
            print(f"⏭️  Skipping {model_name} (already tried)")
            continue  # Skip models that already failed
            
        config = models_config[model_name]
        api_key = os.getenv(config["api_key_env"])
        
        if not api_key:
            print(f"⚠️ {config['name']} - API key not configured ({config['api_key_env']})")
            continue
        
        if api_key:
            try:
                # Create model string with provider prefix
                if model_name == "gemini":
                    full_model = f"google/{config['model']}"
                elif model_name == "groq":
                    full_model = f"groq/{config['model']}"
                elif model_name == "together":
                    full_model = f"together_ai/{config['model']}"
                elif model_name == "huggingface":
                    full_model = f"huggingface/{config['model']}"
                elif model_name == "openrouter":
                    full_model = f"openrouter/{config['model']}"
                elif model_name == "mistral":
                    full_model = f"mistral/{config['model']}"
                else:
                    full_model = config['model']
                
                return LLM(
                    model=full_model,
                    api_key=api_key,
                    max_retries=2,  # Reduced to fail faster
                    timeout=120,  # Reduced timeout
                    temperature=0.7
                )
            except ImportError as e:
                print(f"⚠️ {config['name']} initialization failed: {str(e)}")
                print(f"   ℹ️  This provider requires 'litellm'. Run: pip install litellm")
                continue
            except Exception as e:
                print(f"⚠️ {config['name']} initialization failed: {str(e)}")
                continue
    
    # No API keys found
    raise ValueError(
        "No free-tier LLM API keys found!\n\n"
        "This app uses FREE TIER models with automatic fallback.\n"
        "Please set at least one of:\n"
        "- GROQ_API_KEY (Groq Llama 3.1) - ⭐ RECOMMENDED - UNLIMITED free tier\n"
        "- TOGETHER_API_KEY (Together AI) - $25 free credits (~10K requests)\n"
        "- HUGGINGFACE_API_KEY (HuggingFace) - 1000 requests/day free\n"
        "- GOOGLE_API_KEY (Gemini 2.5 Flash) - 10 req/min free\n"
        "- OPENROUTER_API_KEY (OpenRouter Llama 3.1) - Limited free tier\n"
        "- MISTRAL_API_KEY (Mistral Small) - Limited free tier\n\n"
        "Get keys here:\n"
        "- Groq: https://console.groq.com/keys (RECOMMENDED)\n"
        "- Gemini: https://aistudio.google.com/app/apikey\n"
        "- OpenRouter: https://openrouter.ai/keys\n"
        "- Mistral: https://console.mistral.ai/api-keys"
    )

# Initialize LLM with fallback support
gemini_llm = get_llm()

search_tool = SerperDevTool()

def create_news_scout_agent(llm):
    """Factory function to create news scout agent with given LLM"""
    today = datetime.now().strftime("%B %d, %Y")
    return Agent(
        role='Tech News Analyst',
        goal=f'Find 7-10 diverse tech news stories published today ({today}) covering AI/ML, cybersecurity, startups, software/cloud, and industry news. Include both global and Indian tech news. Only use stories from the last 24 hours. No duplicates.',
        backstory='Expert tech journalist covering global and Indian technology. Searches by topic and geography for balanced coverage.',
        tools=[search_tool],
        verbose=True,
        llm=llm,
        max_iter=12,
        max_execution_time=600,
        allow_delegation=False
    )

def create_company_researcher_agent(llm):
    """Factory function to create company researcher agent with given LLM"""
    return Agent(
        role='Interview Prep Researcher',
        goal='Research a company thoroughly and create an interview prep briefing with killer questions.',
        backstory='Elite interview coach who researches companies deeply to help candidates ask impressive, specific questions.',
        tools=[search_tool],
        verbose=True,
        llm=llm,
        max_iter=12,
        max_execution_time=480
    )

# Agent 1: The News Scout
news_scout = create_news_scout_agent(gemini_llm)

# Agent 2: The Interview Strategist
company_researcher = create_company_researcher_agent(gemini_llm)

from elevenlabs.client import ElevenLabs
from elevenlabs import save

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def _pick_voice_id(preferred_id, preferred_name):
    if preferred_id:
        return preferred_id

    try:
        voices = client.voices.get_all()
        if not voices or not getattr(voices, "voices", None):
            return None

        if preferred_name:
            for voice in voices.voices:
                if voice.name and voice.name.lower() == preferred_name.lower():
                    return voice.voice_id

        return voices.voices[0].voice_id
    except Exception as e:
        print(f"⚠️ ElevenLabs voices unavailable: {str(e)[:80]}")
        return None

def _is_truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def _extract_audio_summary(text, max_items):
    if not text:
        return ""

    items = []

    if "📰" in text:
        parts = text.split("📰")
        for part in parts[1:]:
            cleaned = part.strip()
            if not cleaned:
                continue
            first_line = cleaned.splitlines()[0].strip()
            if first_line:
                items.append(first_line)
            if len(items) >= max_items:
                break

    if not items:
        for line in (line.strip() for line in text.splitlines() if line.strip()):
            if line.startswith(("- ", "• ")):
                items.append(line.lstrip("-• ").strip())
            else:
                items.append(line)
            if len(items) >= max_items:
                break

    if not items:
        return text

    summary_lines = ["Audio summary:"] + [f"- {item}" for item in items]
    return "\n".join(summary_lines)

def _strip_markdown_for_speech(text):
    """Remove markdown/HTML formatting so TTS reads clean prose."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove markdown headers (## Header → Header)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers (**, __, *, _)
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove inline code backticks
    text = re.sub(r'`([^`]*)`', r'\1', text)
    # Remove markdown links [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove bullet markers (-, •, *) at line start → keep the text
    text = re.sub(r'^[\s]*[-•*]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered list markers (1. 2. etc) → keep the text
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def _build_audio_text(text):
    use_summary = _is_truthy(os.getenv("AUDIO_USE_SUMMARY", "true"))
    max_items = _safe_int(os.getenv("AUDIO_SUMMARY_ITEMS", "50"), 50)
    max_chars = _safe_int(os.getenv("AUDIO_MAX_CHARS", "10000"), 10000)

    text_to_speak = _extract_audio_summary(text, max_items) if use_summary else text
    text_to_speak = _strip_markdown_for_speech(text_to_speak)

    if max_chars > 0 and len(text_to_speak) > max_chars:
        text_to_speak = text_to_speak[:max_chars].rstrip()

    return text_to_speak

def speak_text(text):
    """Generate audio from text using ElevenLabs (preferred) or gTTS (fallback), then send to Telegram"""
    text_to_speak = _build_audio_text(text)
    if not text_to_speak.strip():
        print("⚠️ Audio text is empty. Skipping audio generation.")
        return

    audio_file = "/tmp/daily_brief.mp3"

    # --- Try ElevenLabs first ---
    elevenlabs_ok = False
    try:
        preferred_voice_id = "21m00Tcm4TlvDq8ikWAM" #australian female 
        preferred_voice_name = os.getenv("ELEVENLABS_VOICE_NAME", "Rachel")
        voice_id = _pick_voice_id(preferred_voice_id, preferred_voice_name)
        

        if voice_id:
            print("🎙️ Generating audio with ElevenLabs...")
            audio = client.text_to_speech.convert(
                text=text_to_speak,
                voice_id=voice_id,
                model_id="eleven_turbo_v2_5"
            )
            save(audio, audio_file)
            print(f"✅ ElevenLabs audio saved to {audio_file}")
            elevenlabs_ok = True
        else:
            print("⚠️ No ElevenLabs voice available, falling back to gTTS.")
    except Exception as el_err:
        print(f"⚠️ ElevenLabs failed: {str(el_err)[:120]}")
        print("🔄 Falling back to gTTS (Google Text-to-Speech)...")

    # --- Fall back to gTTS ---
    if not elevenlabs_ok:
        try:
            from gtts import gTTS
            print("🎙️ Generating audio with gTTS (female voice)...")
            tts = gTTS(text=text_to_speak, lang="en", tld="com.au", slow=False)  # co.uk = British female voice
            tts.save(audio_file)
            print(f"✅ gTTS audio saved to {audio_file}")
        except Exception as gtts_err:
            print(f"⚠️ gTTS also failed: {gtts_err}")
            print("Continuing without audio...")
            return

    # --- Send to Telegram ---
    send_telegram_audio(audio_file)



def send_telegram_audio(audio_file_path):
    """Send audio file to Telegram"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Telegram credentials not set. Skipping audio...")
        return
    
    try:
        import requests
        import certifi
        url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'chat_id': chat_id, 'title': 'Daily Tech Brief'}
            response = requests.post(url, files=files, data=data, verify=certifi.where())
            
            if response.status_code == 200:
                print("✅ Audio sent to Telegram")
                return True
            else:
                print(f"❌ Failed to send audio: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to send audio to Telegram: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_telegram(text):
    """Send message to Telegram, splitting if needed"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Telegram credentials not set. Skipping...")
        return
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Telegram has 4096 character limit per message
        MAX_LENGTH = 4000  # Leave some buffer
        
        if len(text) <= MAX_LENGTH:
            # Send as single message
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            response = requests.post(url, data=data)
            if response.status_code != 200:
                print(f"❌ Telegram API error: {response.status_code} - {response.text}")
                return False
            print(f"✅ Telegram message sent ({len(text)} chars)")
            return True
        else:
            # Split into multiple messages
            print(f"⚠️ Message too long ({len(text)} chars). Splitting...")
            
            # Split by double newlines to keep stories together
            parts = text.split('\n\n')
            current_chunk = ""
            chunk_count = 0
            
            for part in parts:
                if len(current_chunk) + len(part) + 2 <= MAX_LENGTH:
                    current_chunk += part + "\n\n"
                else:
                    # Send current chunk
                    if current_chunk:
                        chunk_count += 1
                        data = {"chat_id": chat_id, "text": current_chunk, "parse_mode": "HTML"}
                        response = requests.post(url, data=data)
                        if response.status_code != 200:
                            print(f"❌ Telegram chunk {chunk_count} failed: {response.text}")
                        else:
                            print(f"✅ Sent chunk {chunk_count} ({len(current_chunk)} chars)")
                    # Start new chunk
                    current_chunk = part + "\n\n"
            
            # Send final chunk
            if current_chunk:
                chunk_count += 1
                data = {"chat_id": chat_id, "text": current_chunk, "parse_mode": "HTML"}
                response = requests.post(url, data=data)
                if response.status_code != 200:
                    print(f"❌ Telegram chunk {chunk_count} failed: {response.text}")
                else:
                    print(f"✅ Sent chunk {chunk_count} ({len(current_chunk)} chars)")
            
            print(f"✅ All {chunk_count} Telegram chunks sent")
            return True
            
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        import traceback
        traceback.print_exc()
        return False