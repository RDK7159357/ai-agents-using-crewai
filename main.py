from crewai import Task, Crew
from agents import news_scout, company_researcher, speak_text, send_telegram

def daily_brief():
    task = Task(
        description="Summarize the most important technology news from the last 24 hours. Cover multiple topics across AI, software engineering, startups, cybersecurity, hardware, and emerging technologies. Focus on impactful stories that matter to tech professionals.",
        expected_output="A comprehensive, engaging briefing covering 5-10 key technology developments in a conversational style.",
        agent=news_scout
    )
    crew = Crew(agents=[news_scout], tasks=[task])
    result = crew.kickoff()
    
    # Format and send to Telegram
    message = f"<b>🤖 AI Daily Brief</b>\n\n{result.raw}"
    send_telegram(message)
    speak_text(result.raw)

def interview_prep(company):
    task = Task(
        description=f"Research {company}. Focus on their engineering blog and AI stack.",
        expected_output="5 specific talking points to impress an interviewer.",
        agent=company_researcher
    )
    crew = Crew(agents=[company_researcher], tasks=[task])
    result = crew.kickoff()
    
    # Format and send to Telegram
    message = f"<b>💼 Interview Prep: {company}</b>\n\n{result.raw}"
    send_telegram(message)
    print(result.raw)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "interview":
        if len(sys.argv) > 2:
            interview_prep(sys.argv[2])
        else:
            print("Usage: python main.py interview <company_name>")
    else:
        daily_brief()