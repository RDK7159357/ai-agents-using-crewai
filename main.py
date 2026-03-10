from crewai import Task, Crew, LLM
from agents import news_scout, company_researcher, speak_text, send_telegram, get_llm, reset_tried_models, create_news_scout_agent, create_company_researcher_agent
import time
import re
import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables from .env file
load_dotenv()

def get_ollama_llm():
    """Get Ollama LLM using CrewAI's native LLM class.
    
    Uses the openai/ prefix with a custom base_url pointing to Ollama's
    OpenAI-compatible /v1 endpoint. This ensures base_url is correctly
    passed through to LiteLLM instead of defaulting to platform.openai.com.
    """
    api_url = os.getenv("OLLAMA_API_URL", "https://ollama.com/api/chat")
    api_key = os.getenv("OLLAMA_API_KEY")
    model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
    
    if not api_key:
        return None
    
    # Derive the OpenAI-compatible base URL from the Ollama API URL
    base_url = api_url.replace("/api/chat", "/v1").rstrip("/")
    
    # Prefix with openai/ so LiteLLM routes to the custom base_url
    full_model = f"openai/{model}" if not model.startswith("openai/") else model
    
    try:
        return LLM(
            model=full_model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            timeout=180,
        )
    except Exception as e:
        print(f"⚠️ Ollama LLM initialization failed: {e}")
        return None

def format_for_telegram(text):
    """Convert markdown formatting to Telegram HTML, safely handling special characters"""
    # Escape HTML special characters first (except those we'll use for formatting)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Remove horizontal rules (---, ___, ***)
    text = re.sub(r'^[\s]*[-_*]{3,}[\s]*$', '', text, flags=re.MULTILINE)
    
    # Convert markdown tables to readable text
    # First, detect and remove table separator rows (|---|---|)
    text = re.sub(r'^\s*\|[\s\-:|]+\|\s*$', '', text, flags=re.MULTILINE)
    # Convert table header/data rows: | Col1 | Col2 | -> "Col1: Col2"
    def format_table_row(match):
        row = match.group(0)
        cells = [c.strip() for c in row.strip('| \t').split('|')]
        cells = [c for c in cells if c]
        if len(cells) == 2:
            return f"• <b>{cells[0]}</b>: {cells[1]}"
        elif len(cells) >= 3:
            return "• " + " | ".join(cells)
        elif len(cells) == 1:
            return f"• {cells[0]}"
        return row
    text = re.sub(r'^\s*\|.+\|\s*$', format_table_row, text, flags=re.MULTILINE)
    
    # Convert ## headers to bold (must be done before ** conversion)
    text = re.sub(r'^#{1,6}\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
    
    # Convert **bold** to <b>bold</b> (must be done before single *)
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    
    # Convert *italic* to <i>italic</i> (but not if it's part of **)
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    
    # Convert `code` to <code>code</code>
    text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)
    
    # Clean up excessive blank lines (more than 2 in a row)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    # Clean up lines that are just whitespace
    text = re.sub(r'\n\s+\n', '\n\n', text)
    
    return text.strip()

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
    
    # Count unique news stories by extracting headlines after 📰
    headlines = re.findall(r'📰\s*\*?\*?([^\n*]+)', output_text)
    # Normalize and deduplicate headlines
    seen = set()
    unique_headlines = []
    for h in headlines:
        normalized = h.strip().lower()
        # Consider headlines with >60% word overlap as duplicates
        is_dup = False
        for s in seen:
            words_h = set(normalized.split())
            words_s = set(s.split())
            if words_h and words_s:
                overlap = len(words_h & words_s) / max(len(words_h), len(words_s))
                if overlap > 0.6:
                    is_dup = True
                    break
        if not is_dup:
            seen.add(normalized)
            unique_headlines.append(h.strip())
    
    story_count = len(unique_headlines)
    
    if story_count < 5:
        return False, f"Only {story_count} unique stories found, minimum is 5"
    
    # Check for Indian tech content
    india_keywords = ['india', 'indian', 'mumbai', 'bangalore', 'delhi', 'bengaluru', 'hyderabad',
                      'chennai', 'pune', 'startup india', 'upi', 'nasscom', 'infosys', 'tcs', 'wipro',
                      'reliance', 'jio', 'flipkart', 'zomato', 'phonepe', 'razorpay', 'zerodha']
    has_india = any(keyword in lower_output for keyword in india_keywords)
    
    if not has_india:
        return False, "No Indian tech news found"
    
    # Check for global tech content
    global_keywords = ['google', 'apple', 'microsoft', 'meta', 'amazon', 'nvidia', 'openai',
                       'tesla', 'samsung', 'us ', 'china', 'europe', 'eu ', 'silicon valley',
                       'deepmind', 'anthropic', 'global', 'worldwide']
    has_global = any(keyword in lower_output for keyword in global_keywords)
    
    if not has_global:
        return False, "No global tech news found"
    
    # Check topic diversity — flag if ALL stories are product launches / shopping deals
    consumer_keywords = ['launch', 'launched', 'specifications', 'specs', 'smartwatch', 'smartphone',
                         'sale', 'discount', 'offers', 'price', 'flipkart', 'amazon sale']
    diverse_keywords = ['ai ', 'artificial intelligence', 'machine learning', 'cybersecurity', 'security',
                        'vulnerability', 'breach', 'funding', 'raised', 'valuation', 'acquisition',
                        'open source', 'cloud', 'layoff', 'regulation', 'policy', 'software']
    
    has_diverse = any(kw in lower_output for kw in diverse_keywords)
    if not has_diverse:
        return False, "No topic diversity — all stories appear to be product launches or shopping deals"
    
    return True, f"Valid output with {story_count} unique stories"

def clean_interview_preamble(output_text):
    """Strip any preamble or meta-instructions before the actual content."""
    if not output_text:
        return output_text

    # Find the first section header (e.g. "**COMPANY", "COMPANY INTEL", "**1.")
    match = re.search(r'(?:^|\n)\s*(?:\*\*)?(?:COMPANY|1[.\)])', output_text)
    if match and match.start() > 0:
        preamble = output_text[:match.start()].strip()
        if len(preamble) > 50:
            output_text = output_text[match.start():].lstrip()

    # Strip trailing meta-commentary
    lines = output_text.rstrip().split('\n')
    meta_tails = [
        'every bullet', 'the final answer', 'no generic', 'follow the exact',
        'no extra commentary', 'must contain specific', 'critical:', 'do not use placeholder',
        'do not copy these instructions',
    ]
    while lines and any(p in lines[-1].lower() for p in meta_tails):
        lines.pop()
    return '\n'.join(lines).rstrip()

def validate_interview_output(output_text):
    """Validate that interview prep output contains actual research, not raw tool calls, unfilled templates, or parroted instructions."""
    if not output_text or len(output_text.strip()) < 200:
        return False, "Output too short (less than 200 characters)"

    lower_output = output_text.lower()

    # Detect raw tool call syntax leaked into the output
    tool_call_patterns = [
        'search_the_internet_with_serper',
        '<search_',
        'search_query',
        'search_type',
        '</function>',
        'action_input',
        'action: search',
        'please wait for the results',
        'i need to search',
        'let me search',
        'i will now search',
        'i\'ll search for',
    ]
    tool_call_count = sum(1 for p in tool_call_patterns if p in lower_output)
    if tool_call_count >= 2:
        return False, f"Output contains raw tool call syntax ({tool_call_count} patterns detected) instead of actual results"

    # Detect unfilled template placeholders like [year], [city], [X], [Name]
    placeholder_pattern = re.findall(r'\[(?:year|city|state|country|X|Name|specific|brief|Language|Framework|Cloud|version|Date|Source)\w*[^\]]*\]', output_text, re.IGNORECASE)
    if len(placeholder_pattern) >= 3:
        return False, f"Output contains {len(placeholder_pattern)} unfilled template placeholders: {placeholder_pattern[:5]}"

    # Detect template/instruction text being parroted back verbatim
    instruction_phrases = [
        'list every technology, framework',
        'founding year, hq location, employee count',
        'for each piece of intel above',
        'generate at least 5',
        'craft a sharp question',
        'how this makes you stand out',
        'when to drop each fact naturally',
        'how to close strong by referencing',
        'what to say if asked',
        'for each section, give 2-3 sentences',
        'exact versions if available',
        'real technical and business challenges they face',
        'team size, work style (remote/hybrid/onsite)',
        'examples of great questions',
        'adapt to',
        'do not copy these instructions',
        'every fact must come from your search',
    ]
    parrot_count = sum(1 for p in instruction_phrases if p in lower_output)
    if parrot_count >= 4:
        return False, f"Output is parroting {parrot_count} instruction phrases back instead of providing researched data"

    # Reject outputs where most sections are "Not found" — means agent skipped searches
    not_found_count = lower_output.count('not found in public sources')
    if not_found_count >= 4:
        return False, f"Agent was lazy: {not_found_count} out of 7 sections say 'Not found'. Agent must run all searches."

    # Check that output has substantive content
    has_bullets = output_text.count('•') >= 3 or output_text.count('-') >= 5
    has_structure = '**' in output_text or any(f'{i}.' in output_text for i in range(1, 8))
    if not has_bullets and not has_structure:
        return False, "Output lacks structured talking points"

    return True, "Valid interview prep output"

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

def run_crew_with_rate_limit_retry(crew, model_name, max_rate_retries=3):
    """Run a crew kickoff with automatic wait-and-retry on 429 rate limit errors."""
    for attempt in range(max_rate_retries + 1):
        try:
            return crew.kickoff()
        except Exception as e:
            error_str = str(e)
            if is_rate_limit_error(error_str) and attempt < max_rate_retries:
                base_wait = extract_retry_wait_seconds(error_str, default=90)
                wait_secs = base_wait + (attempt * 45)  # Exponential backoff: +0s, +45s, +90s
                print(f"\n⏳ Rate limit hit on {model_name} (attempt {attempt+1}/{max_rate_retries}). "
                      f"Waiting {wait_secs}s before retry...")
                time.sleep(wait_secs)
                print(f"🔄 Retrying {model_name} after rate limit cooldown...")
                continue
            raise  # Re-raise if not rate limit or out of retries

def get_current_model_name(llm):
    """Extract model name from LLM object"""
    # Check if it's Ollama LLM
    if isinstance(llm, OllamaLLM):
        return "ollama"
    
    model_str = llm.model if hasattr(llm, 'model') else str(llm)
    # Extract the model name from formats like "groq/llama-3.1-8b-instant"
    if '/' in model_str:
        parts = model_str.split('/')
        model_name = parts[0]  # e.g., "groq", "google", "openrouter", "mistral"
        return model_name
    return "unknown"

def extract_model_provider(model_string):
    """Extract provider short name from model string"""
    # Handle Ollama
    if model_string == "ollama":
        return "ollama"
    
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
    """Execute daily brief with runtime fallback mechanism - Ollama first"""
    print("🚀 Starting daily brief...")
    
    # Check for Ollama API key first
    ollama_llm = get_ollama_llm()
    
    # Diagnose available API keys
    available_keys = []
    if ollama_llm:
        available_keys.append("ollama")
    
    for key_name in ["GOOGLE_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "MISTRAL_API_KEY"]:
        if os.getenv(key_name):
            available_keys.append(key_name.replace("_API_KEY", "").lower())
    
    print(f"🔑 Available API keys: {', '.join(available_keys) if available_keys else 'NONE!'}")
    
    if not available_keys:
        send_telegram("❌ <b>Configuration Error</b>\n\n<i>No API keys found! Please configure at least one of: OLLAMA_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, MISTRAL_API_KEY</i>")
        return
    
    # Show which model is being used
    if ollama_llm:
        print(f"🤖 Primary Model: Ollama ({ollama_llm.model}) with automatic fallback to Gemini/Groq/OpenRouter/Mistral")
    else:
        preferred = os.getenv("PREFERRED_MODEL", "gemini")
        print(f"🤖 Model: {preferred} (Gemini 2.5 Flash with automatic runtime fallback)")
    
    # Add delay to avoid rate limits
    time.sleep(2)
    
    # Reset tried models for this execution
    reset_tried_models()
    tried_models = set()
    max_retries = 5  # Increased to 5: ollama + gemini + groq + openrouter + mistral
    current_attempt = 0
    
    while current_attempt < max_retries:
        current_attempt += 1
        
        try:
            # Try Ollama first, then fall back to other models
            if current_attempt == 1 and ollama_llm:
                current_llm = ollama_llm
                current_model = "ollama"
                print(f"\n📡 Attempt {current_attempt}/{max_retries} using Ollama ({ollama_llm.model})...")
            else:
                # Fall back to other LLMs
                if current_attempt == 1:
                    # If Ollama not available, skip to attempt 2
                    current_attempt += 1
                
                current_llm = get_llm(skip_models=tried_models)
                current_model = extract_model_provider(current_llm.model)
                print(f"\n📡 Attempt {current_attempt}/{max_retries} using {current_model}...")
            
            # Add progressive backoff delay for retries
            if current_attempt > 1:
                delay = (current_attempt - 1) * 30  # 30s, 60s, 90s, 120s
                print(f"⏱️  Waiting {delay}s before retry to avoid rate limits...")
                time.sleep(delay)
            
            # Create fresh agent with current LLM
            fresh_news_scout = create_news_scout_agent(current_llm)
            
            task = Task(
                description="""Find and summarize the most important, SPECIFIC technology news from the last 24 hours.

CRITICAL: TOPIC DIVERSITY IS MANDATORY.
You MUST cover a MIX of these categories. Do NOT focus only on product launches or shopping deals.

REQUIRED TOPIC MIX (at least one story from EACH category):
1. AI / Machine Learning — new models, research breakthroughs, industry adoption (search: "AI news today", "machine learning breakthrough", "LLM release")
2. Software Engineering / Cloud — developer tools, open source, cloud platforms, programming languages (search: "software engineering news", "open source release", "cloud computing news")  
3. Cybersecurity — breaches, vulnerabilities, security tools, regulations (search: "cybersecurity news today", "data breach", "security vulnerability")
4. Startups & Funding — funding rounds, acquisitions, IPOs (search: "startup funding today", "tech acquisition", "Indian startup funding")
5. Industry / Business — Big Tech earnings, layoffs, policy, regulation (search: "tech industry news", "Big Tech news today")

BANNED: Do NOT fill the brief with only smartphone launches, e-commerce sales, or gadget reviews.
At most 1-2 stories can be about consumer device launches. The rest MUST be from the categories above.

GEOGRAPHIC COVERAGE (MANDATORY — search for EACH separately):
- At least 3-4 global stories (search: "global tech news today", "Silicon Valley news", "Europe tech news", "China tech news", "US technology news today")
- At least 3-4 Indian tech stories (search: "India tech news today", "Indian startup funding", "India technology policy", "Bangalore tech news", "Indian IT industry news", "India AI news")
- Indian stories should cover: Indian startups, funding rounds, NASSCOM/IT industry, government tech policy (Digital India, UPI, ONDC), Indian tech companies (Infosys, TCS, Wipro, Reliance Jio, Flipkart, Zomato, PhonePe, etc.)
- Global stories should cover: Big Tech (Google, Apple, Microsoft, Meta, Amazon), US/EU/China tech developments, global AI race, international cybersecurity

OTHER REQUIREMENTS:
- MUST return MINIMUM 7-10 news stories (mandatory)
- Include SPECIFIC company names, product names, version numbers
- Cite CONCRETE numbers: funding amounts, user counts, performance metrics
- Reference REAL announcements with specific dates
- Every story MUST be UNIQUE — absolutely NO duplicate or repeated stories
- Perform SEPARATE searches for each topic category above to ensure diversity

Your response must start directly with the first 📰 story. No preamble, no commentary, no instructions — just the stories.""",
                expected_output="""7-10 UNIQUE news stories covering DIVERSE topics. NO duplicates.

MANDATORY: At least 1 story from EACH of these: AI/ML, Software/Cloud, Cybersecurity, Startups/Funding, Industry/Business.
At most 1-2 product launch stories. The rest must be from the categories above.

Structure each story as:
        
📰 **[Specific Product/Company Name]: [What Happened]**
• Concrete detail 1 (with numbers, names, or specifications)
• Concrete detail 2 (actual feature, metric, or announcement)
• Why it matters (specific impact, use case, or implication)

Example AI/ML Story:
📰 **OpenAI Releases GPT-5 with 10 Trillion Parameters**
• Launched on February 3, 2026 with 10 trillion parameters (5x larger than GPT-4)
• Benchmarks show 40% improvement in code generation accuracy on HumanEval
• Why it matters: First model to pass the ARC-AGI benchmark, suggesting progress toward general reasoning

Example Cybersecurity Story:
📰 **Critical Linux Kernel Vulnerability (CVE-2026-XXXX) Actively Exploited**
• Remote code execution flaw in kernel 6.x networking stack, CVSS score 9.8
• CISA adds to Known Exploited Vulnerabilities catalog, patches available
• Why it matters: Affects all major cloud providers; urgent patching required for production servers

Example Indian Startup Story:
📰 **Zepto Raises $350M Series F at $5B Valuation**
• Mumbai-based quick commerce startup closed funding on February 3, 2026
• Plans to expand dark store network from 350 to 700 stores by June 2026
• Why it matters: Largest quick-commerce funding in India, intensifies competition with Blinkit and Instamart

Example Global Tech Story:
📰 **Google DeepMind Announces Gemini Ultra 2 with Real-Time Video Understanding**
• New multimodal model processes live video streams at 60fps with 95% accuracy
• Available via API at $0.01/1K tokens, undercutting GPT-5 pricing by 30%
• Why it matters: First production-ready model for real-time video analysis at scale

Example Indian Tech Story:
📰 **PhonePe Crosses 800M Registered Users, Expands into Stock Broking**
• Walmart-backed fintech now processes 60% of India's UPI transactions
• Launched Share.Market platform targeting India's growing retail investor base
• Why it matters: PhonePe's diversification beyond payments signals India's fintech maturation

ABSOLUTE RULE: Each story must appear EXACTLY ONCE. Never repeat a story.
MUST HAVE: At least 3 global stories AND at least 3 Indian tech stories. This is non-negotiable.""",

                agent=fresh_news_scout
            )
            
            # Configure crew with limits to reduce API usage
            crew = Crew(
                agents=[fresh_news_scout], 
                tasks=[task],
                max_rpm=2,  # Very conservative: ~2 reqs/min to stay within free-tier rate limits
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
            
            # Clean up any preamble the LLM may have added before the first story
            raw_output = result.raw
            first_story = raw_output.find('📰')
            if first_story > 0:
                raw_output = raw_output[first_story:]
            
            # Format and send to Telegram with proper HTML formatting
            from datetime import datetime
            today = datetime.now().strftime("%B %d, %Y")
            
            formatted_content = format_for_telegram(raw_output)
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
    
    # Check for Ollama API key first
    ollama_llm = get_ollama_llm()
    
    # Reset tried models for this execution
    reset_tried_models()
    tried_models = set()
    max_retries = 5  # Try all models: ollama, gemini, groq, openrouter, mistral
    current_attempt = 0
    
    while current_attempt < max_retries:
        current_attempt += 1
        
        # Try Ollama first, then fall back to other models
        if current_attempt == 1 and ollama_llm:
            current_llm = ollama_llm
            current_model = "ollama"
            print(f"\n📡 Attempt {current_attempt}/{max_retries} using Ollama ({ollama_llm.model})...")
        else:
            # Get next LLM to try - Prefer Gemini for interview prep (higher context limit)
            # Skip Groq initially to avoid TPM limits
            if current_attempt == 1 and not ollama_llm:
                # First attempt without Ollama: Force Gemini (2M context) and skip Groq
                tried_models.add("groq")  # Skip Groq on first attempt
                current_llm = get_llm(skip_models=tried_models, prefer_model="gemini")
            elif current_attempt == 2 and ollama_llm:
                # Second attempt after Ollama: Force Gemini and skip Groq
                tried_models.add("groq")  # Skip Groq on second attempt
                current_llm = get_llm(skip_models=tried_models, prefer_model="gemini")
            else:
                # Subsequent attempts: Try remaining models including Groq
                if "groq" in tried_models and (current_attempt == 3 or (current_attempt == 2 and not ollama_llm)):
                    tried_models.remove("groq")  # Allow Groq on retry
                current_llm = get_llm(skip_models=tried_models, prefer_model="gemini")
            
            current_model = extract_model_provider(current_llm.model)
            print(f"\n📡 Attempt {current_attempt}/{max_retries} using {current_model}...")
        
        # Add delay to avoid rate limits
        time.sleep(2)
        
        try:
            # Create a fresh agent with the current LLM so fallback actually switches models
            interview_agent = create_company_researcher_agent(current_llm)
            
            task = Task(
                description=f"""You are preparing a candidate for a job interview at {company}.

You MUST perform EXACTLY 6 searches before writing your answer. Do NOT skip any search. Do NOT write your final answer until all 6 searches are complete.

SEARCH 1: Search for "{company} company overview founded headquarters CEO employees"
SEARCH 2: Search for "{company} technology stack software engineering tools"
SEARCH 3: Search for "{company} latest news 2025 2026 announcements"
SEARCH 4: Search for "{company} glassdoor reviews engineering culture work environment"
SEARCH 5: Search for "{company} competitors challenges industry problems"
SEARCH 6: Search for "{company} careers jobs hiring engineering positions"

After completing ALL 6 searches, compile your findings into this briefing:

COMPANY INTEL: founding year, HQ city, employee count, what {company} does, CEO and CTO names.

TECH STACK: every technology, language, framework, database, cloud service you found in job postings or articles.

RECENT MOVES: 3-5 events from the last 12 months with dates and numbers.

CULTURE & TEAM: team size, remote/hybrid/onsite, Glassdoor rating, employee review themes.

CHALLENGES: business problems, competitors, technical difficulties.

KILLER QUESTIONS TO ASK INTERVIEWER: 5-7 smart questions. Each must reference a specific {company} fact you found. After each question explain why it impresses the interviewer.

INTERVIEW PLAYBOOK: How to answer "Why {company}?" using your findings. When to mention specific facts. How to close strong.

IMPORTANT: You have the search tool. USE IT for all 6 searches. The more you search, the better the briefing. Do not say "Not found" without actually searching first.

FORMAT: Use plain text with bullet points (•) and bold (**text**) for headers. Do NOT use markdown tables (| col | col |) or ## headers. Keep it clean and readable.""",
                expected_output=f"""A detailed {company} intelligence briefing with all sections populated from search results, at least 5 killer interviewer questions, and interview tactics.""",
                agent=interview_agent
            )
            
            crew = Crew(
                agents=[interview_agent], 
                tasks=[task],
                max_rpm=10,
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Validate result before sending
            if not result or not result.raw or len(result.raw.strip()) < 100:
                raise Exception(f"Incomplete result from {current_model}: only {len(result.raw) if result and result.raw else 0} characters")
            
            is_valid, validation_msg = validate_interview_output(result.raw)
            if not is_valid:
                print(f"⚠️ Output validation failed: {validation_msg}")
                raise Exception(f"Output validation failed for {current_model}: {validation_msg}")
            
            # Clean up preamble/meta-instructions before sending
            cleaned_output = clean_interview_preamble(result.raw)
            
            # Success! Format and send to Telegram
            from datetime import datetime
            today = datetime.now().strftime("%B %d, %Y")
            
            formatted_content = format_for_telegram(cleaned_output)
            message = f"""<b>🎯 Interview Edge: {company}</b>
<i>Prepared on {today} | Your unfair advantage</i>

{formatted_content}

<i>━━━━━━━━━━━━━━━━</i>
<i>Go crush it! 🔥</i>"""
            send_telegram(message)
            
            # Try audio generation but don't fail if it doesn't work
            try:
                speak_text(cleaned_output)
            except Exception as audio_error:
                print(f"⚠️ Audio generation failed: {audio_error}")
                print("But interview prep was sent successfully!")
            
            print(f"\n✅ Interview prep completed successfully with {current_model}!")
            print(cleaned_output)
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
