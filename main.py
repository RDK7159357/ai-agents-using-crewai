from crewai import Task, Crew
from agents import news_scout, company_researcher, speak_text, send_telegram
import time
import re

def format_for_telegram(text):
    """Convert markdown formatting to Telegram HTML"""
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Convert *italic* to <i>italic</i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Convert __bold__ to <b>bold</b>
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    # Convert _italic_ to <i>italic</i>
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    return text

def daily_brief():
    print("🚀 Starting daily brief...")
    
    # Add delay to avoid rate limits
    time.sleep(2)
    
    task = Task(
        description="Summarize the most important technology news from the last 24 hours. Cover multiple topics across AI, software engineering, startups, cybersecurity, hardware, and emerging technologies. Focus on impactful stories that matter to tech professionals. Format each story with a clear title and brief description.",
        expected_output="""A well-structured briefing with 5-10 key technology developments. Format each story as:
        
📰 [Story Title]
[2-3 sentence summary explaining the key details and why it matters]

Keep it conversational, engaging, and focused on actionable insights for tech professionals.""",
        agent=news_scout
    )
    crew = Crew(agents=[news_scout], tasks=[task])
    
    try:
        result = crew.kickoff()
        
        # Format and send to Telegram with proper HTML formatting
        from datetime import datetime
        today = datetime.now().strftime("%B %d, %Y")
        
        formatted_content = format_for_telegram(result.raw)
        message = f"""<b>🤖 Tech Daily Brief</b>
<i>{today}</i>

{formatted_content}

<i>━━━━━━━━━━━━━━━━</i>
<i>Powered by AI Agent</i>"""
        send_telegram(message)
        speak_text(result.raw)
    except Exception as e:
        error_msg = f"Error during daily brief: {e}"
        print(error_msg)
        if "429" in str(e) or "TooManyRequests" in str(e):
            print("\n⚠️  Rate limit hit. Waiting 60 seconds before retry...")
            time.sleep(60)
            print("Retrying...")
            result = crew.kickoff()
            from datetime import datetime
            today = datetime.now().strftime("%B %d, %Y")
            formatted_content = format_for_telegram(result.raw)
            message = f"""<b>🤖 Tech Daily Brief</b>
<i>{today}</i>

{formatted_content}

<i>━━━━━━━━━━━━━━━━</i>
<i>Powered by AI Agent</i>"""
            send_telegram(message)
            speak_text(result.raw)

def interview_prep(company):
    print(f"🚀 Starting interview prep for {company}...")
    
    # Add delay to avoid rate limits
    time.sleep(2)
    
    task = Task(
        description=f"Research {company}. Focus on their engineering blog, tech stack, recent innovations, and company culture. Find concrete, specific information that would help in an interview.",
        expected_output="""5 specific, actionable talking points formatted as:
        
💡 [Talking Point Title]
[2-3 sentences with specific details, facts, or insights that demonstrate knowledge of the company]

Focus on recent developments, technical choices, and opportunities to add value.""",
        agent=company_researcher
    )
    crew = Crew(agents=[company_researcher], tasks=[task])
    
    try:
        result = crew.kickoff()
        
        # Format and send to Telegram
        from datetime import datetime
        today = datetime.now().strftime("%B %d, %Y")
        
        formatted_content = format_for_telegram(result.raw)
        message = f"""<b>💼 Interview Prep: {company}</b>
<i>Prepared on {today}</i>

{formatted_content}

<i>━━━━━━━━━━━━━━━━</i>
<i>Good luck! 🍀</i>"""
        send_telegram(message)
        print(result.raw)
    except Exception as e:
        error_msg = f"Error during interview prep: {e}"
        print(error_msg)
        if "429" in str(e) or "TooManyRequests" in str(e):
            print("\n⚠️  Rate limit hit. Waiting 60 seconds before retry...")
            time.sleep(60)
            print("Retrying...")
            result = crew.kickoff()
            from datetime import datetime
            today = datetime.now().strftime("%B %d, %Y")
            formatted_content = format_for_telegram(result.raw)
            message = f"""<b>💼 Interview Prep: {company}</b>
<i>Prepared on {today}</i>

{formatted_content}

<i>━━━━━━━━━━━━━━━━</i>
<i>Good luck! 🍀</i>"""
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