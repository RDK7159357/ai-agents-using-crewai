from dotenv import load_dotenv
import os
import time
from crewai import Agent, LLM
from crewai_tools import SerperDevTool

load_dotenv()

# Track which models have already been tried to avoid infinite loops
_models_tried = set()

def reset_tried_models():
    """Reset the list of tried models for retry logic"""
    global _models_tried
    _models_tried = set()

def get_llm(skip_models=None):
    """
    Get LLM with fallback support.
    Tries models in order based on PREFERRED_MODEL setting.
    Set PREFERRED_MODEL in .env to override (gemini, groq, openrouter, mistral)
    
    Args:
        skip_models: Set of model names to skip (used for fallback retries)
    """
    if skip_models is None:
        skip_models = set()
    
    preferred_model = os.getenv("PREFERRED_MODEL", "gemini").lower()
    
    models_config = {
        "gemini": {
            "model": "gemini-2.5-flash",
            "api_key_env": "GOOGLE_API_KEY",
            "name": "Gemini 2.5 Flash",
            "free_tier": "10 req/min"
        },
        "groq": {
            "model": "llama-3.1-8b-instant",
            "api_key_env": "GROQ_API_KEY",
            "name": "Groq Llama 3.1 8B Instant",
            "free_tier": "unlimited"
        },
        "openrouter": {
            "model": "upstage/solar-pro-3:free",
            "api_key_env": "OPENROUTER_API_KEY",
            "name": "OpenRouter Solar Pro 3 (free)",
            "free_tier": "limited"
        },
        "mistral": {
            "model": "mistral-small-latest",
            "api_key_env": "MISTRAL_API_KEY",
            "name": "Mistral Small Latest",
            "free_tier": "limited"
        }
    }
    
    # Fallback order: Try Gemini 2.5 Flash first, then fallbacks
    fallback_order = ["gemini", "groq", "openrouter", "mistral"]
    
    # Move preferred model to front if specified
    if preferred_model in models_config and preferred_model != "gemini":
        fallback_order.remove(preferred_model)
        fallback_order.insert(0, preferred_model)
    
    # Try each model in order (skip already-tried ones)
    for model_name in fallback_order:
        if model_name in skip_models:
            continue  # Skip models that already failed
            
        config = models_config[model_name]
        api_key = os.getenv(config["api_key_env"])
        
        if api_key:
            try:
                print(f"🤖 Using {config['name']} ({config['free_tier']})")
                
                # Create model string with provider prefix
                if model_name == "gemini":
                    full_model = f"google/{config['model']}"
                elif model_name == "groq":
                    full_model = f"groq/{config['model']}"
                elif model_name == "openrouter":
                    full_model = f"openrouter/{config['model']}"
                elif model_name == "mistral":
                    full_model = f"mistral/{config['model']}"
                else:
                    full_model = config['model']
                
                return LLM(
                    model=full_model,
                    api_key=api_key,
                    max_retries=3,
                    timeout=180,
                    temperature=0.7
                )
            except Exception as e:
                print(f"⚠️ {config['name']} initialization failed: {str(e)}")
                continue
    
    # No API keys found
    raise ValueError(
        "No free-tier LLM API keys found!\n\n"
        "This app uses FREE TIER models with automatic fallback.\n"
        "Please set at least one of:\n"
        "- GROQ_API_KEY (Groq Llama 3.1) - RECOMMENDED - unlimited free tier\n"
        "- GOOGLE_API_KEY (Gemini 1.5 Flash)\n"
        "- OPENROUTER_API_KEY (OpenRouter Llama 3.1)\n"
        "- MISTRAL_API_KEY (Mistral Small)\n\n"
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
    return Agent(
        role='Technology Trends Analyst',
        goal='Identify the most important and interesting technology developments from the last 24 hours across all tech domains and geographies, with special focus on both global and Indian tech ecosystems.',
        backstory='An expert researcher who filters signal from noise in technology news globally. Covers AI/ML, software engineering, startups, hardware, cybersecurity, and emerging tech from Silicon Valley to Bangalore. Particularly skilled at finding concrete details and diverse geographic perspectives, ensuring both global innovation and Indian tech ecosystem developments are captured.',
        tools=[search_tool],
        verbose=True,
        llm=llm,
        max_iter=15,  # Increased to allow thorough searching for multiple stories
        max_execution_time=600  # 10 minute timeout for comprehensive research
    )

def create_company_researcher_agent(llm):
    """Factory function to create company researcher agent with given LLM"""
    return Agent(
        role='Corporate Value Analyst',
        goal='Research {company_name} to find technical challenges I can help solve.',
        backstory='A specialist in engineering interviews who finds "value-add" angles.',
        tools=[search_tool],
        verbose=True,
        llm=llm,
        max_iter=8,  # Limit iterations to reduce API calls
        max_execution_time=300  # 5 minute timeout
    )

# Agent 1: The News Scout
news_scout = create_news_scout_agent(gemini_llm)

# Agent 2: The Interview Strategist
company_researcher = create_company_researcher_agent(gemini_llm)

from elevenlabs.client import ElevenLabs
from elevenlabs import save

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def speak_text(text):
    """Generate audio from text using ElevenLabs and send to Telegram"""
    try:
        # Truncate text to avoid hitting API limits
        text_to_speak = text[:500] if len(text) > 500 else text
        
        print("🎙️ Generating audio...")
        audio = client.text_to_speech.convert(
            text=text_to_speak,
            voice_id="nPczCjzI2devNBz1zQrb",  # Brian voice ID
            model_id="eleven_monolingual_v1"
        )
        
        # Save audio to file
        audio_file = "/tmp/daily_brief.mp3"
        save(audio, audio_file)
        print(f"✅ Audio saved to {audio_file}")
        
        # Send to Telegram
        send_telegram_audio(audio_file)
        
    except Exception as e:
        print(f"⚠️ Audio generation failed: {str(e)}")
        print("Continuing without audio...")

def send_telegram_audio(audio_file_path):
    """Send audio file to Telegram"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Telegram credentials not set. Skipping audio...")
        return
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'chat_id': chat_id, 'title': 'Daily Tech Brief'}
            response = requests.post(url, files=files, data=data)
            
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