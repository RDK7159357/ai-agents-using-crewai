from crewai import Task, Crew
from agents import news_scout, company_researcher, speak_text, send_telegram, get_llm, reset_tried_models, create_news_scout_agent
import time
import re
import os

def format_for_telegram(text):
    """Convert markdown formatting to Telegram HTML, safely handling special characters"""
    # Escape HTML special characters first (except those we'll use for formatting)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Convert **bold** to <b>bold</b> (must be done before single *)
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    
    # Convert *italic* to <i>italic</i> (but not if it's part of **)
    # Only match single * that aren't already part of HTML tags
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    
    # Clean up any remaining standalone * or _ that aren't formatting
    # (This handles bullet points like "• ")
    
    return text

def get_current_model_name(llm):
    """Extract model name from LLM object"""
    model_str = llm.model if hasattr(llm, 'model') else str(llm)
    # Extract the model name from formats like "groq/llama-3.1-8b-instant"
    if '/' in model_str:
        parts = model_str.split('/')
        model_name = parts[0]  # e.g., "groq", "google", "openrouter", "mistral"
        return model_name
    return "unknown"

def extract_model_provider(model_string):
    """Extract provider short name from model string"""
    # Handle format: "google/gemini-2.5-flash" -> "gemini"
    if '/' in model_string:
        provider = model_string.split('/')[0]
        provider_map = {
            "google": "gemini",
            "groq": "groq",
            "openrouter": "openrouter",
            "mistral": "mistral"
        }
        return provider_map.get(provider, provider)
    
    # Handle format: "gemini-2.5-flash" or "llama-3.1-8b-instant" -> extract base name
    # Map model names to their short names
    if model_string.startswith("gemini"):
        return "gemini"
    elif model_string.startswith("llama"):
        return "groq"
    elif model_string.startswith("mistral"):
        return "mistral"
    elif "meta-llama" in model_string:
        return "openrouter"
    
    return model_string

def daily_brief():
    """Execute daily brief with runtime fallback mechanism"""
    print("🚀 Starting daily brief...")
    
    # Diagnose available API keys
    available_keys = []
    for key_name in ["GOOGLE_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "MISTRAL_API_KEY"]:
        if os.getenv(key_name):
            available_keys.append(key_name.replace("_API_KEY", "").lower())
    
    print(f"🔑 Available API keys: {', '.join(available_keys) if available_keys else 'NONE!'}")
    
    if not available_keys:
        send_telegram("❌ <b>Configuration Error</b>\n\n<i>No API keys found! Please configure at least one of: GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, MISTRAL_API_KEY</i>")
        return
    
    # Show which model is being used
    preferred = os.getenv("PREFERRED_MODEL", "gemini")
    print(f"🤖 Model: {preferred} (Gemini 2.5 Flash with automatic runtime fallback)")
    
    # Add delay to avoid rate limits
    time.sleep(2)
    
    # Reset tried models for this execution
    reset_tried_models()
    tried_models = set()
    max_retries = 4  # Increased to 4 to try all models: gemini, groq, openrouter, mistral
    current_attempt = 0
    
    while current_attempt < max_retries:
        current_attempt += 1
        
        try:
            # Get LLM with fallback to untried models
            current_llm = get_llm(skip_models=tried_models)
            current_model = extract_model_provider(current_llm.model)
            
            print(f"\n📡 Attempt {current_attempt}/{max_retries} using {current_model}...")
            
            # Add progressive backoff delay for retries
            if current_attempt > 1:
                delay = (current_attempt - 1) * 5  # 5s, 10s, 15s
                print(f"⏱️  Waiting {delay}s before retry to avoid rate limits...")
                time.sleep(delay)
            
            # Create fresh agent with current LLM
            fresh_news_scout = create_news_scout_agent(current_llm)
            
            task = Task(
                description="""Find and summarize the most important, SPECIFIC technology news from the last 24 hours. 
        
CRITICAL REQUIREMENTS:
- MUST return MINIMUM 5-10 news stories (this is mandatory, not optional)
- MUST include BOTH global tech news AND Indian tech news
- Cover diverse topics: AI/ML, software engineering, startups, cybersecurity, hardware, emerging tech
- Include SPECIFIC company names, product names, and version numbers
- Cite CONCRETE numbers: funding amounts, user counts, performance metrics, percentages
- Mention ACTUAL features, capabilities, or technical specifications
- Reference REAL announcements, launches, or releases with specific dates
- Include WHO (company/person), WHAT (specific product/feature), WHY it matters (with concrete impact)

GEOGRAPHIC COVERAGE:
- At least 3-5 global stories (US, Europe, China, etc.)
- At least 2-3 Indian tech stories (startups, funding, tech policy, Indian companies)
- Search for: "India tech news today", "Indian startup funding", "India technology"
        
Avoid generic statements. Every story must have verifiable, specific details.
DO NOT return just 1-2 stories. You MUST find and return 5-10 distinct news items.""",
                expected_output="""MINIMUM 5-10 news stories with SPECIFIC details. MUST include both global and Indian tech news.

Structure each story as:
        
📰 **[Specific Product/Company Name]: [What Happened]**
• Concrete detail 1 (with numbers, names, or specifications)
• Concrete detail 2 (actual feature, metric, or announcement)
• Why it matters (specific impact, use case, or implication)

Example Global Story:
📰 **OpenAI Releases GPT-5 with 10 Trillion Parameters**
• Launched on February 3, 2026 with 10 trillion parameters (5x larger than GPT-4)
• New multimodal capabilities process video at 60fps, up from 30fps
• Benchmarks show 40% improvement in code generation accuracy on HumanEval
• Priced at $0.03 per 1K tokens, 25% cheaper than GPT-4 Turbo
• Why it matters: First model to pass the ARC-AGI benchmark, suggesting progress toward general reasoning

Example Indian Story:
📰 **Zepto Raises $350M Series F at $5B Valuation**
• Mumbai-based quick commerce startup closed funding on February 3, 2026
• Led by Nexus Venture Partners and existing investors Glade Brook Capital
• Plans to expand dark store network from 350 to 700 stores by June 2026
• Currently processing 2M orders/day across 10 cities with 12-minute average delivery
• Why it matters: Largest quick-commerce funding in India, intensifies competition with Blinkit and Instamart

You MUST provide AT LEAST 5 stories total. Include diverse topics covering:
- Global tech (AI, cloud, cybersecurity, hardware)
- Indian startups & funding rounds
- Indian tech policy & regulations
- Product launches (global and India-specific)

DO NOT use vague phrases like "continues to be important" or "experts say". Every point needs specifics.""",
                agent=fresh_news_scout
            )
            
            # Configure crew with limits to reduce API usage
            crew = Crew(
                agents=[fresh_news_scout], 
                tasks=[task],
                max_rpm=10,  # Max 10 requests per minute
                verbose=True
            )
            
            # Execute the task
            result = crew.kickoff()
            
            # Validate result before sending
            if not result or not result.raw or len(result.raw.strip()) < 100:
                raise Exception(f"Incomplete result from {current_model}: only {len(result.raw) if result and result.raw else 0} characters")
            
            # Format and send to Telegram with proper HTML formatting
            from datetime import datetime
            today = datetime.now().strftime("%B %d, %Y")
            
            formatted_content = format_for_telegram(result.raw)
            message = f"""<b>🤖 Tech Daily Brief</b>
<i>{today}</i>

{formatted_content}

<i>━━━━━━━━━━━━━━━━</i>
<i>Powered by AI Agent ({current_model})</i>"""
            send_telegram(message)
            
            # Try audio generation but don't fail if it doesn't work
            try:
                speak_text(result.raw)
            except Exception as audio_error:
                print(f"⚠️ Audio generation failed: {audio_error}")
                print("But news brief was sent successfully!")
            
            print(f"✅ Daily brief completed successfully with {current_model}!")
            return  # Success - exit the retry loop
            
        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            print(f"\n❌ Error with {current_model}: [{error_type}] {error_str[:200]}")
            
            # Track this model as tried
            tried_models.add(current_model)
            
            # Check if we should retry with next model
            if current_attempt < max_retries:
                print(f"⚠️ Switching to next model...")
                time.sleep(2)  # Brief delay before retry
                continue  # Try next model - don't send error notification yet
            else:
                # All retries exhausted - send error notification
                print(f"\n❌ All {max_retries} attempts failed. No more models to try.")
                
                # Send Telegram notification only after all attempts fail
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "TooManyRequests" in error_str or "RateLimitError" in error_str or "rate_limited" in error_str:
                    send_telegram(f"⚠️ <b>Rate Limit Error</b>\n\n<code>{error_type}: {error_str[:400]}</code>\n\n<i>All configured LLM models have hit rate limits. Please wait and try again later, or add more API keys.</i>")
                    print("\n🔧 Rate limit solutions:")
                    print("1. Wait 24 hours for quota reset")
                    print("2. Add more API keys to .env file")
                    print("3. Upgrade to paid API tiers")
                else:
                    send_telegram(f"❌ <b>Critical Error in Daily Brief</b>\n\n<b>Task execution failed:</b> <code>{error_type}: {error_str[:400]}</code>\n\n<i>All fallback models failed. Please check API keys and try again.</i>")
                    print(f"\n🔧 Troubleshooting:")
                    print("1. Verify all API keys in .env file")
                    print("2. Check API key validity and quota")
                    print("3. Ensure internet connection is working")

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
• Bu
    # Configure crew with limits to reduce API usage
    crew = Crew(
        agents=[company_researcher], 
        tasks=[task],
        max_rpm=10,  # Max 10 requests per minute
        verbose=True
    osts by 35%
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
        
        # Check if it's a rate limit error
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "TooManyRequests" in str(e):
            send_telegram(f"⚠️ <b>Rate Limit Error</b>\n\n{str(e)[:500]}\n\n<i>This usually means you've exceeded the Gemini API free tier quota.\n\nPlease wait and try again later, or upgrade to a paid tier.</i>")
            print("\n❌ Rate limit exceeded. Cannot retry - quota exhausted.")
            print("\nSolutions:")
            print("1. Wait 24 hours for quota reset")
            print("2. Upgrade to paid Gemini API tier")
            print("3. Switch to gemini-1.5-flash (1500 req/day free tier)")
        else:
            # For other errors, send error notification
            send_telegram(f"❌ <b>Error in Interview Prep</b>\n\n<code>{str(e)[:500]}</code>")

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