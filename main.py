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
        description="""Find and summarize the most important, SPECIFIC technology news from the last 24 hours. 
        
REQUIREMENTS:
- Include SPECIFIC company names, product names, and version numbers
- Cite CONCRETE numbers: funding amounts, user counts, performance metrics, percentages
- Mention ACTUAL features, capabilities, or technical specifications
- Reference REAL announcements, launches, or releases with specific dates
- Include WHO (company/person), WHAT (specific product/feature), WHY it matters (with concrete impact)
        
Avoid generic statements. Every story must have verifiable, specific details.
Cover AI, software engineering, startups, cybersecurity, hardware, and emerging tech.""",
        expected_output="""5-10 news stories with SPECIFIC details. Each story must include:
        
📰 **[Specific Product/Company Name]: [What Happened]**
• Concrete detail 1 (with numbers, names, or specifications)
• Concrete detail 2 (actual feature, metric, or announcement)
• Why it matters (specific impact, use case, or implication)

Example:
📰 **OpenAI Releases GPT-5 with 10 Trillion Parameters**
• Launched on February 3, 2026 with 10 trillion parameters (5x larger than GPT-4)
• New multimodal capabilities process video at 60fps, up from 30fps
• Benchmarks show 40% improvement in code generation accuracy on HumanEval
• Priced at $0.03 per 1K tokens, 25% cheaper than GPT-4 Turbo
• Why it matters: First model to pass the ARC-AGI benchmark, suggesting progress toward general reasoning

DO NOT use vague phrases like "continues to be important" or "experts say". Every point needs specifics.""",
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
        description=f"""Research {company} and find SPECIFIC, CONCRETE information for interview preparation.
        
REQUIREMENTS:
- Identify SPECIFIC technologies in their stack (exact versions, frameworks, tools)
- Find RECENT developments: latest product launches, features, acquisitions (with dates)
- Discover CONCRETE metrics: revenue, user numbers, growth rates, market position
- Reference ACTUAL blog posts, GitHub repos, tech talks (with titles and dates)
- Identify SPECIFIC challenges or problems they're solving
- Find REAL examples of their engineering culture, practices, or values
        
Avoid generic advice. Every talking point must be verifiable and specific to {company}.""",
        expected_output=f"""5 specific, well-researched talking points with CONCRETE details:
        
💡 **[Specific Topic/Technology]**
• Specific fact 1 (with numbers, dates, or exact technologies)
• Specific fact 2 (actual product feature, blog post title, or initiative)
• How to use this in interview (concrete question to ask or value to demonstrate)

Example:
💡 **Their Kubernetes Migration at Scale**
• Migrated 10,000+ microservices to Kubernetes 1.28 in Q4 2025 (mentioned in Dec 2025 blog post)
• Built custom autoscaler "ScaleX" that reduced compute costs by 35%
• Open-sourced their service mesh configuration tool on GitHub (2,300+ stars)
• Interview angle: Ask about their approach to observability during the migration, mention experience with similar scale challenges

Every point should reference actual, verifiable information about {company}.""",
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
    
    # Check if running in bot mode
    if len(sys.argv) > 1 and sys.argv[1] == "bot":
        from telegram_bot import TelegramBot
        bot = TelegramBot(daily_brief, interview_prep)
        bot.start()
    
    # Check if running interview prep from CLI
    elif len(sys.argv) > 1 and sys.argv[1] == "interview":
        if len(sys.argv) > 2:
            interview_prep(sys.argv[2])
        else:
            print("Usage: python main.py interview <company_name>")
    
    # Default: run daily brief
    else:
        daily_brief()