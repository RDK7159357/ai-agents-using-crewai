#!/usr/bin/env python3
"""
LLM API Testing Script
Tests Gemini, Groq, OpenRouter, and Mistral API keys
"""

import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style
import time

# Initialize colorama for colored output
init(autoreset=True)

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text:^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_info(text):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def test_gemini_15_flash():
    """Test Gemini 1.5 Flash API"""
    print_header("Testing Gemini 1.5 Flash API")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print_warning("GOOGLE_API_KEY not set in .env file")
        print_info("Get free API key: https://aistudio.google.com/app/apikey")
        print_info("Free tier: 1,500 requests/day")
        return False
    
    try:
        from crewai import LLM
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-4:]}")
        print_info("Initializing Gemini 1.5 Flash...")
        
        llm = LLM(
            model="google/gemini-1.5-flash",
            api_key=api_key,
            max_retries=1,
            timeout=30
        )
        
        print_info("Sending test prompt: 'Say hello'")
        start_time = time.time()
        
        response = llm.call([{"role": "user", "content": "Say hello in one word"}])
        
        elapsed = time.time() - start_time
        
        print_success(f"✓ Response received in {elapsed:.2f} seconds")
        print_info(f"Response: {response[:100]}")
        print_success("Gemini 1.5 Flash API is working!")
        print_info("Free tier: 1,500 requests/day ✨")
        
        return True
        
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        
        if "401" in str(e) or "Unauthorized" in str(e):
            print_error("Invalid API key")
            print_info("Check your GOOGLE_API_KEY in .env file")
        elif "429" in str(e) or "quota" in str(e).lower():
            print_error("Rate limit exceeded")
            print_info("You've used your daily quota (1,500 requests/day)")
            print_info("Wait 24 hours or upgrade to paid tier")
        elif "403" in str(e) or "Forbidden" in str(e):
            print_error("API key doesn't have access to this model")
            print_info("Regenerate your API key at https://aistudio.google.com/app/apikey")
        
        return False

def test_gemini_25_flash():
    """Test Gemini 2.5 Flash API"""
    print_header("Testing Gemini 2.5 Flash API")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print_warning("GOOGLE_API_KEY not set in .env file")
        return False
    
    try:
        from crewai import LLM
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-4:]}")
        print_info("Initializing Gemini 2.5 Flash...")
        
        llm = LLM(
            model="google/gemini-2.5-flash",
            api_key=api_key,
            max_retries=1,
            timeout=30
        )
        
        print_info("Sending test prompt: 'Say hello'")
        start_time = time.time()
        
        response = llm.call([{"role": "user", "content": "Say hello in one word"}])
        
        elapsed = time.time() - start_time
        
        print_success(f"✓ Response received in {elapsed:.2f} seconds")
        print_info(f"Response: {response[:100]}")
        print_success("Gemini 2.5 Flash API is working!")
        print_warning("Limited quota: Only 20 requests/day ⚠️")
        print_info("Use Gemini 1.5 Flash for daily automation (1,500 req/day)")
        
        return True
        
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        
        if "429" in str(e) or "quota" in str(e).lower():
            print_error("Rate limit exceeded")
            print_warning("Gemini 2.5 Flash only allows 20 requests/day")
            print_info("Use Gemini 1.5 Flash instead (1,500 req/day)")
        
        return False

def test_groq():
    """Test Groq API"""
    print_header("Testing Groq API (Llama 3.1 8B Instant)")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print_warning("GROQ_API_KEY not set in .env file")
        print_info("Get API key: https://console.groq.com/keys")
        print_info("Free tier available")
        return None
    
    try:
        from crewai import LLM
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-4:]}")
        print_info("Initializing Groq Llama 3.1 8B Instant...")
        
        llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=api_key,
            max_retries=1,
            timeout=30
        )
        
        print_info("Sending test prompt: 'Say hello'")
        start_time = time.time()
        
        response = llm.call([{"role": "user", "content": "Say hello in one word"}])
        
        elapsed = time.time() - start_time
        
        print_success(f"✓ Response received in {elapsed:.2f} seconds")
        print_info(f"Response: {response[:100]}")
        print_success("Groq API is working!")
        print_info("Free tier available ✨")
        
        return True
        
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        
        if "401" in str(e) or "Unauthorized" in str(e):
            print_error("Invalid API key")
            print_info("Check your GROQ_API_KEY in .env file")
        elif "429" in str(e):
            print_error("Rate limit exceeded")
            print_info("Check your usage: https://console.groq.com/")
        
        return False

def test_openrouter():
    """Test OpenRouter API"""
    print_header("Testing OpenRouter API (Gemma 4 31B Free)")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print_warning("OPENROUTER_API_KEY not set in .env file")
        print_info("Get API key: https://openrouter.ai/keys")
        print_info("Free tier available")
        return None
    
    try:
        from crewai import LLM
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-4:]}")
        print_info("Initializing OpenRouter Gemma 4 31B Free...")
        
        llm = LLM(
            model="openrouter/google/gemma-4-31b-it:free",
            api_key=api_key,
            max_retries=1,
            timeout=30
        )
        
        print_info("Sending test prompt: 'Say hello'")
        start_time = time.time()
        
        response = llm.call([{"role": "user", "content": "Say hello in one word"}])
        
        elapsed = time.time() - start_time
        
        print_success(f"✓ Response received in {elapsed:.2f} seconds")
        print_info(f"Response: {response[:100]}")
        print_success("OpenRouter API is working!")
        print_info("Free tier available ✨")
        
        return True
        
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        
        if "401" in str(e) or "Unauthorized" in str(e):
            print_error("Invalid API key")
            print_info("Check your OPENROUTER_API_KEY in .env file")
        elif "429" in str(e):
            print_error("Rate limit exceeded")
            print_info("Check your usage: https://openrouter.ai/keys")
        
        return False

def test_mistral():
    """Test Mistral API"""
    print_header("Testing Mistral API (Mistral Small Latest)")
    
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print_warning("MISTRAL_API_KEY not set in .env file")
        print_info("Get API key: https://console.mistral.ai/api-keys")
        print_info("Free tier available")
        return None
    
    try:
        from crewai import LLM
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-4:]}")
        print_info("Initializing Mistral Small Latest...")
        
        llm = LLM(
            model="mistral/mistral-small-latest",
            api_key=api_key,
            max_retries=1,
            timeout=30
        )
        
        print_info("Sending test prompt: 'Say hello'")
        start_time = time.time()
        
        response = llm.call([{"role": "user", "content": "Say hello in one word"}])
        
        elapsed = time.time() - start_time
        
        print_success(f"✓ Response received in {elapsed:.2f} seconds")
        print_info(f"Response: {response[:100]}")
        print_success("Mistral API is working!")
        print_info("Free tier available ✨")
        
        return True
        
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        
        if "401" in str(e) or "Unauthorized" in str(e):
            print_error("Invalid API key")
            print_info("Check your MISTRAL_API_KEY in .env file")
        elif "429" in str(e):
            print_error("Rate limit exceeded")
            print_info("Check your usage: https://console.mistral.ai/")
        
        return False

def print_summary(results):
    """Print test summary"""
    print_header("Summary")
    
    print(f"\n{Fore.CYAN}Free Tier Models:{Style.RESET_ALL}")
    if results.get("gemini_25"):
        print_success("Gemini 2.5 Flash: Working ✓ (20 req/day FREE)")
    else:
        print_error("Gemini 2.5 Flash: Failed ✗")
    
    print(f"\n{Fore.CYAN}Additional Free Tier Providers (Optional):{Style.RESET_ALL}")
    if results.get("groq") is None:
        print_info("Groq: Not configured (optional)")
    elif results.get("groq"):
        print_success("Groq: Working ✓")
    else:
        print_error("Groq: Failed ✗")
    
    if results.get("openrouter") is None:
        print_info("OpenRouter: Not configured (optional)")
    elif results.get("openrouter"):
        print_success("OpenRouter: Working ✓")
    else:
        print_error("OpenRouter: Failed ✗")
    
    if results.get("mistral") is None:
        print_info("Mistral: Not configured (optional)")
    elif results.get("mistral"):
        print_success("Mistral: Working ✓")
    else:
        print_error("Mistral: Failed ✗")
    
    print("\n" + "─" * 70)
    
    if results.get("gemini_25"):
        print_success("\n✨ You're all set! Gemini 2.5 Flash is working.")
        print_info("This is the FREE tier model (20 requests/day)")
        print_info("For higher volume, consider using other providers with unlimited free tiers.")
        print_info("\nYou can now run: python main.py")
    else:
        print_error("\n⚠️  No LLM API is working - at least one is required!")
        print_info("\nTo fix Gemini:")
        print_info("1. Get free API key: https://aistudio.google.com/app/apikey")
        print_info("2. Add to .env: GOOGLE_API_KEY=your-key-here")
        print_info("3. Install LiteLLM: pip install litellm")
        print_info("4. Run this test again: python test_llm_apis.py")

def main():
    """Run all LLM API tests"""
    print(f"{Fore.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║              LLM API TESTING SCRIPT                               ║")
    print("║     Test Gemini, Groq, OpenRouter, Mistral Keys                  ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print_error(".env file not found!")
        print_info("Create a .env file with your API keys")
        print_info("See .env.example for template")
        sys.exit(1)
    
    results = {}
    
    # Test free tier models
    print_info("Testing FREE tier models first...\n")
    results["gemini_25"] = test_gemini_25_flash()
    
    # Test additional free-tier providers (optional)
    print_info("\nTesting additional free-tier providers (optional)...\n")
    results["groq"] = test_groq()
    results["openrouter"] = test_openrouter()
    results["mistral"] = test_mistral()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if results.get("gemini_25"):
        sys.exit(0)  # Success - at least Gemini works
    else:
        sys.exit(1)  # Failure - need at least one LLM

if __name__ == "__main__":
    main()
