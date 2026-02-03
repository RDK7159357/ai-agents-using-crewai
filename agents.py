from dotenv import load_dotenv
import os
from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Initialize Gemini LLM
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

search_tool = SerperDevTool()

# Agent 1: The News Scout
news_scout = Agent(
    role='AI Trends Analyst',
    goal='Identify the top 3 AI breakthroughs from the last 24 hours.',
    backstory='An expert researcher who filters signal from noise in AI/ML.',
    tools=[search_tool],
    verbose=True,
    llm=gemini_llm
)

# Agent 2: The Interview Strategist
company_researcher = Agent(
    role='Corporate Value Analyst',
    goal='Research {company_name} to find technical challenges I can help solve.',
    backstory='A specialist in engineering interviews who finds "value-add" angles.',
    tools=[search_tool],
    verbose=True,
    llm=gemini_llm
)

from elevenlabs.client import ElevenLabs
from elevenlabs import play

client = ElevenLabs(ElevenLabs.api_key_from_env(), cache_root="cache")

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