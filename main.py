from crewai import Task, Crew
from agents import news_scout, company_researcher, speak_text, send_telegram, get_llm, reset_tried_models, create_news_scout_agent
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

def validate_news_output(output_text):
    """Validate that the output contains sufficient news stories"""
    if not output_text or len(output_text.strip()) < 200:
        return False, "Output too short (less than 200 characters)"
    
    # Check if output is just a meta-message about needing to search
    meta_phrases = [
        "doesn't meet the requirements",
        "call another tool",
        "let's search",
        "need to find",
        "i should search",
        "i need to"
    ]
    lower_output = output_text.lower()
    for phrase in meta_phrases:
        if phrase in lower_output and len(output_text) < 1000:
            return False, f"Output appears to be a meta-message, not actual news (contains '{phrase}')"
    
    # Count news stories (look for 📰 emoji or numbered items)
    story_count = output_text.count('📰') + output_text.count('**1.')  + output_text.count('**2.') + output_text.count('**3.')
    
    if story_count < 5:
        return False, f"Only {story_count} stories found, minimum is 5"
    
    # Check for Indian tech content
    india_keywords = ['india', 'indian', 'mumbai', 'bangalore', 'delhi', 'bengaluru', 'hyderabad']
    has_india = any(keyword in lower_output for keyword in india_keywords)
    
    if not has_india:
        return False, "No Indian tech news found"
    
    return True, f"Valid output with {story_count} stories"

def extract_retry_wait_seconds(error_str, default=65):
    """Parse the retry delay from a 429 error message"""
    import re
    # Try to find 'Please retry in Xs' pattern
    match = re.search(r'retry[^\d]+(\d+(?:\.\d+)?)', error_str, re.IGNORECASE)
    if match:
        return max(int(float(match.group(1))) + 5, default)  # Add 5s buffer
    return default

def is_rate_limit_error(error_str):
    """Check if the error is a rate limit error"""
    rate_limit_indicators = ["429", "RESOURCE_EXHAUSTED", "TooManyRequests",
                              "RateLimitError", "rate_limited", "rate limit"]
    return any(ind.lower() in error_str.lower() for ind in rate_limit_indicators)

def run_crew_with_rate_limit_retry(crew, model_name, max_rate_retries=2):
    """Run a crew kickoff with automatic wait-and-retry on 429 rate limit errors."""
    for attempt in range(max_rate_retries + 1):
        try:
            return crew.kickoff()
        except Exception as e:
            error_str = str(e)
            if is_rate_limit_error(error_str) and attempt < max_rate_retries:
                wait_secs = extract_retry_wait_seconds(error_str, default=65)
                print(f"\n⏳ Rate limit hit on {model_name} (attempt {attempt+1}/{max_rate_retries}). "
                      f"Waiting {wait_secs}s before retry...")
                time.sleep(wait_secs)
                print(f"🔄 Retrying {model_name} after rate limit cooldown...")
                continue
            raise  # Re-raise if not rate limit or out of retries

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
        
IMPORTANT: You MUST complete this task. Do NOT return meta-messages like 'I need to search more' or 'this doesn't meet requirements'. 
Perform multiple searches if needed, then compile and return the actual news stories.
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
                max_rpm=4,  # Conservative: ~4 reqs/min leaves buffer below Gemini's 15 req/min limit
                verbose=True
            )
            
            # Execute the task with rate-limit retry
            result = run_crew_with_rate_limit_retry(crew, current_model)
            
            # Validate result before sending
            if not result or not result.raw or len(result.raw.strip()) < 100:
                raise Exception(f"Incomplete result from {current_model}: only {len(result.raw) if result and result.raw else 0} characters")
            
            # Additional validation to ensure quality output
            is_valid, validation_msg = validate_news_output(result.raw)
            if not is_valid:
                raise Exception(f"Output validation failed for {current_model}: {validation_msg}")
            
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
    
    # Reset tried models for this execution
    reset_tried_models()
    tried_models = set()
    max_retries = 4  # Try all models: gemini, groq, openrouter, mistral
    current_attempt = 0
    
    while current_attempt < max_retries:
        current_attempt += 1
        
        # Get next LLM to try - Prefer Gemini for interview prep (higher context limit)
        # Skip Groq initially to avoid TPM limits
        if current_attempt == 1:
            # First attempt: Force Gemini (2M context) and skip Groq
            tried_models.add("groq")  # Skip Groq on first attempt
            current_llm = get_llm(skip_models=tried_models, prefer_model="gemini")
        else:
            # Subsequent attempts: Try remaining models including Groq
            if "groq" in tried_models and current_attempt == 2:
                tried_models.remove("groq")  # Allow Groq on retry
            current_llm = get_llm(skip_models=tried_models, prefer_model="gemini")
        
        current_model = extract_model_provider(current_llm.model)
        
        print(f"\n📡 Attempt {current_attempt}/{max_retries} using {current_model}...")
        
        # Add delay to avoid rate limits
        time.sleep(2)
        
        try:
            task = Task(
                description=f"""Research {company} for interview prep. Find:
- Tech stack (specific frameworks, versions, tools)
- Recent news (product launches, acquisitions, metrics)
- Engineering culture and challenges
- Concrete, verifiable facts only.""",
                expected_output=f"""5 specific talking points about {company}:

**[Topic]**
• Key fact with details (dates, numbers, technologies)
• How to use in interview

Keep concise. Reference actual information.""",
                agent=company_researcher
            )
            
            crew = Crew(
                agents=[company_researcher], 
                tasks=[task],
                llm=current_llm,
                max_rpm=10,
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Success! Format and send to Telegram
            from datetime import datetime
            today = datetime.now().strftime("%B %d, %Y")
            
            formatted_content = format_for_telegram(result.raw)
            message = f"""<b>💼 Interview Prep: {company}</b>
<i>Prepared on {today}</i>

{formatted_content}

<i>━━━━━━━━━━━━━━━━</i>
<i>Good luck! 🍀</i>"""
            send_telegram(message)
            print(f"\n✅ Interview prep completed successfully with {current_model}!")
            print(result.raw)
            return
            
        except Exception as e:
            error_str = str(e)
            print(f"\n❌ Error with {current_model}: {error_str[:200]}")
            
            # Track this model as tried
            tried_models.add(current_model)
            
            # Check for TPM (tokens per minute) limit - specific to Groq
            is_tpm_error = "tokens per minute" in error_str.lower() or "request too large" in error_str.lower()
            
            # Check if we should retry
            if current_attempt < max_retries:
                if is_tpm_error:
                    print(f"⚠️ TPM limit exceeded with {current_model}. Trying model with higher context...")
                else:
                    print(f"⚠️ Switching to next model...")
                time.sleep(2)  # Brief delay before retry
                continue
            else:
                # All retries exhausted
                print(f"\n❌ All {max_retries} attempts failed. No more models to try.")
                
                # Send error notification only after all attempts fail
                if is_tpm_error:
                    send_telegram(f"⚠️ <b>Context Too Large - Interview Prep</b>\n\n<code>{error_str[:400]}</code>\n\n<i>All models exceeded token limits. Please try again - the system now uses Gemini (higher context) automatically.</i>")
                    print("\n🔧 TPM limit solutions:")
                    print("1. System already using Gemini (highest context)")
                    print("2. Try again in a minute (quota resets)")
                elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "TooManyRequests" in error_str or "rate_limit" in error_str.lower():
                    send_telegram(f"⚠️ <b>Rate Limit Error - Interview Prep</b>\n\n<code>{error_str[:400]}</code>\n\n<i>All configured LLM models have hit rate limits. Please wait and try again later.</i>")
                    print("\n🔧 Rate limit solutions:")
                    print("1. Wait 24 hours for quota reset")
                    print("2. Upgrade to paid API tiers")
                else:
                    send_telegram(f"❌ <b>Critical Error in Interview Prep</b>\n\n<code>{error_str[:400]}</code>\n\n<i>All fallback models failed. Please check API keys.</i>")
                return

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