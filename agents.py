from dotenv import load_dotenv
import os
import time
from crewai import Agent, LLM
from crewai_tools import SerperDevTool

load_dotenv()

def get_llm():
    """
    Get LLM with fallback support.
    Tries models in order based on PREFERRED_MODEL setting.
    Set PREFERRED_MODEL in .env to override (gemini, gemini-2.5, groq, openrouter, mistral)
    """
    preferred_model = os.getenv("PREFERRED_MODEL", "gemini").lower()
    
    models_config = {
        "gemini": {
            "model": "google/gemini-1.5-flash",
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "name": "Gemini 1.5 Flash",
            "free_tier": "1500 req/day"
        },
        "gemini-2.5": {
            "model": "google/gemini-2.5-flash",
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "name": "Gemini 2.5 Flash",
            "free_tier": "20 req/day (experimental)"
        },
        "groq": {
            "model": "groq/llama-3.1-8b-instant",
            "api_key": os.getenv("GROQ_API_KEY"),
            "name": "Groq Llama 3.1 8B Instant",
            "free_tier": "free tier available"
        },
        "openrouter": {
            "model": "openrouter/meta-llama/llama-3.1-8b-instruct",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "name": "OpenRouter Llama 3.1 8B Instruct",
            "free_tier": "free tier available"
        },
        "mistral": {
            "model": "mistral/mistral-small-latest",
            "api_key": os.getenv("MISTRAL_API_KEY"),
            "name": "Mistral Small Latest",
            "free_tier": "free tier available"
        }
    }
    
    # Try preferred model first
    if preferred_model in models_config:
        config = models_config[preferred_model]
        if config["api_key"]:
            print(f"🤖 Using {config['name']} ({config['free_tier']})")
            return LLM(
                model=config["model"],
                api_key=config["api_key"],
                max_retries=3,
                timeout=180,
                temperature=0.7
            )
    
    # Fallback to any available model (FREE TIER ONLY)
    fallback_order = ["gemini", "gemini-2.5", "groq", "openrouter", "mistral"]
    for model_name in fallback_order:
        if model_name == preferred_model:
            continue  # Already tried
        config = models_config[model_name]
        if config["api_key"]:
            print(f"⚠️ Falling back to {config['name']} ({config['free_tier']})")
            return LLM(
                model=config["model"],
                api_key=config["api_key"],
                max_retries=3,
                timeout=180,
                temperature=0.7
            )
    
    # No API keys found
    raise ValueError(
        "No free-tier LLM API keys found!\n\n"
        "This app uses FREE TIER models only.\n"
        "Please set at least one of:\n"
        "- GOOGLE_API_KEY (Gemini 2.5 Flash)\n"
        "- GROQ_API_KEY (Groq Llama 3.1)\n"
        "- OPENROUTER_API_KEY (OpenRouter Llama 3.1)\n"
        "- MISTRAL_API_KEY (Mistral Small)\n\n"
        "Get keys here:\n"
        "- Gemini: https://aistudio.google.com/app/apikey\n"
        "- Groq: https://console.groq.com/keys\n"
        "- OpenRouter: https://openrouter.ai/keys\n"
        "- Mistral: https://console.mistral.ai/api-keys"
    )

# Initialize LLM with fallback support
gemini_llm = get_llm()

search_tool = SerperDevTool()

# Agent 1: The News Scout
news_scout = Agent(
    role='Technology Trends Analyst',
    goal='Identify the most important and interesting technology developments from the last 24 hours across all tech domains and geographies, with special focus on both global and Indian tech ecosystems.',
    backstory='An expert researcher who filters signal from noise in technology news globally. Covers AI/ML, software engineering, startups, hardware, cybersecurity, and emerging tech from Silicon Valley to Bangalore. Particularly skilled at finding concrete details and diverse geographic perspectives, ensuring both global innovation and Indian tech ecosystem developments are captured.',
    tools=[search_tool],
    verbose=True,
    llm=gemini_llm,
    max_iter=15,  # Increased to allow thorough searching for multiple stories
    max_execution_time=600  # 10 minute timeout for comprehensive research
)

# Agent 2: The Interview Strategist
company_researcher = Agent(
    role='Corporate Value Analyst',
    goal='Research {company_name} to find technical challenges I can help solve.',
    backstory='A specialist in engineering interviews who finds "value-add" angles.',
    tools=[search_tool],
    verbose=True,
    llm=gemini_llm,
    max_iter=8,  # Limit iterations to reduce API calls
    max_execution_time=300  # 5 minute timeout
)

from elevenlabs.client import ElevenLabs
from elevenlabs import play

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def speak_text(text):
    audio = client.generate(
        text=text,
        voice="Brian", # High-quality professional voice
        model="eleven_multilingual_v2"
    )
    play(audio)

def send_telegram(text):
    """Send message to Telegram"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Telegram credentials not set. Skipping...")
        return
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")