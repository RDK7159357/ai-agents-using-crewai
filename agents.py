from dotenv import load_dotenv
import os
from crewai import Agent, LLM
from crewai_tools import SerperDevTool

load_dotenv()

# Initialize Gemini LLM using CrewAI's LLM class
gemini_llm = LLM(
    model="gemini-1.5-flash",
    provider="google",
    api_key=os.getenv("GOOGLE_API_KEY")
)

search_tool = SerperDevTool()

# Agent 1: The News Scout
news_scout = Agent(
    role='Technology Trends Analyst',
    goal='Identify the most important and interesting technology developments from the last 24 hours across all tech domains.',
    backstory='An expert researcher who filters signal from noise in technology news, covering AI/ML, software engineering, startups, hardware, cybersecurity, and emerging tech.',
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