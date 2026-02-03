from crewai import Agent
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()

# Agent 1: The News Scout
news_scout = Agent(
    role='AI Trends Analyst',
    goal='Identify the top 3 AI breakthroughs from the last 24 hours.',
    backstory='An expert researcher who filters signal from noise in AI/ML.',
    tools=[search_tool],
    verbose=True
)

# Agent 2: The Interview Strategist
company_researcher = Agent(
    role='Corporate Value Analyst',
    goal='Research {company_name} to find technical challenges I can help solve.',
    backstory='A specialist in engineering interviews who finds "value-add" angles.',
    tools=[search_tool],
    verbose=True
)

from elevenlabs.client import ElevenLabs
from elevenlabs import play

client = ElevenLabs(api_key="YOUR_KEY")

def speak_text(text):
    audio = client.generate(
        text=text,
        voice="Brian", # High-quality professional voice
        model="eleven_multilingual_v2"
    )
    play(audio)