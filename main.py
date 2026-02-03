from crewai import Task, Crew
from agents import news_scout, company_researcher, speak_text

def daily_brief():
    task = Task(
        description="Summarize the most important AI news from the last 24 hours.",
        expected_output="A 2-minute spoken-style briefing.",
        agent=news_scout
    )
    crew = Crew(agents=[news_scout], tasks=[task])
    result = crew.kickoff()
    speak_text(result.raw)

def interview_prep(company):
    task = Task(
        description=f"Research {company}. Focus on their engineering blog and AI stack.",
        expected_output="5 specific talking points to impress an interviewer.",
        agent=company_researcher
    )
    crew = Crew(agents=[company_researcher], tasks=[task])
    result = crew.kickoff()
    print(result.raw) # Usually better to read these points, but you can speak them too!