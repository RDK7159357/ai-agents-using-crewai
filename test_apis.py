#!/usr/bin/env python3
"""
API Testing Script for AI Agent Briefer
Tests all required APIs and shows their status
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

def test_env_variables():
    """Test if environment variables are set"""
    print_header("1. Testing Environment Variables")
    
    load_dotenv()
    
    required_vars = {
        "GOOGLE_API_KEY": "Google Gemini API",
        "SERPER_API_KEY": "Serper Search API",
        "TELEGRAM_BOT_TOKEN": "Telegram Bot Token",
        "TELEGRAM_CHAT_ID": "Telegram Chat ID"
    }
    
    optional_vars = {
        "ELEVENLABS_API_KEY": "ElevenLabs API (voice)",
        "PREFERRED_MODEL": "Model preference"
    }
    
    all_good = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print_success(f"{description}: {masked_value}")
        else:
            print_error(f"{description}: NOT SET")
            all_good = False
    
    print()
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_info(f"{description}: {value}")
        else:
            print_warning(f"{description}: Not set (optional)")
    
    return all_good

def test_gemini_15_flash():
    """Test Gemini 1.5 Flash API"""
    print_header("2. Testing Gemini 1.5 Flash API")
    
    try:
        from crewai import LLM
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print_error("GOOGLE_API_KEY not set")
            return False
        
        print_info("Initializing Gemini 1.5 Flash...")
        llm = LLM(
            model="google/gemini-1.5-flash",
            api_key=api_key,
            max_retries=2,
            timeout=60
        )
        
        print_info("Sending test prompt...")
        start_time = time.time()
        
        # Simple test prompt
        response = llm.call([{"role": "user", "content": "Reply with only: 'API test successful'"}])
        
        elapsed = time.time() - start_time
        
        print_success(f"Response received in {elapsed:.2f}s")
        print_info(f"Response: {response[:100]}...")
        print_success("Gemini 1.5 Flash is working! (1500 req/day free tier)")
        
        return True
        
    except Exception as e:
        print_error(f"Gemini 1.5 Flash test failed: {str(e)}")
        if "429" in str(e):
            print_warning("Rate limit exceeded - you may have used your daily quota")
        return False

def test_gemini_25_flash():
    """Test Gemini 2.5 Flash API"""
    print_header("3. Testing Gemini 2.5 Flash API")
    
    try:
        from crewai import LLM
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print_error("GOOGLE_API_KEY not set")
            return False
        
        print_info("Initializing Gemini 2.5 Flash...")
        llm = LLM(
            model="google/gemini-2.5-flash",
            api_key=api_key,
            max_retries=2,
            timeout=60
        )
        
        print_info("Sending test prompt...")
        start_time = time.time()
        
        response = llm.call([{"role": "user", "content": "Reply with only: 'API test successful'"}])
        
        elapsed = time.time() - start_time
        
        print_success(f"Response received in {elapsed:.2f}s")
        print_info(f"Response: {response[:100]}...")
        print_success("Gemini 2.5 Flash is working! (20 req/day free tier)")
        print_warning("Note: Very limited quota (20/day) - use 1.5 Flash for automation")
        
        return True
        
    except Exception as e:
        print_error(f"Gemini 2.5 Flash test failed: {str(e)}")
        if "429" in str(e):
            print_warning("Rate limit exceeded - Gemini 2.5 only allows 20 requests/day")
        return False

def test_serper():
    """Test Serper search API"""
    print_header("4. Testing Serper Search API")
    
    try:
        from crewai_tools import SerperDevTool
        
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            print_error("SERPER_API_KEY not set")
            return False
        
        print_info("Initializing Serper search tool...")
        search_tool = SerperDevTool()
        
        print_info("Performing test search: 'AI news today'...")
        start_time = time.time()
        
        result = search_tool.run("AI news today")
        
        elapsed = time.time() - start_time
        
        print_success(f"Search completed in {elapsed:.2f}s")
        print_info(f"Results preview: {str(result)[:150]}...")
        print_success("Serper API is working! (2500 searches/month free tier)")
        
        return True
        
    except Exception as e:
        print_error(f"Serper test failed: {str(e)}")
        return False

def test_telegram():
    """Test Telegram bot connection"""
    print_header("5. Testing Telegram Bot")
    
    try:
        import requests
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            print_error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
            return False
        
        print_info("Testing bot authentication...")
        
        # Test getMe endpoint
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_name = bot_info["result"].get("username", "Unknown")
                print_success(f"Bot authenticated: @{bot_name}")
            else:
                print_error("Bot authentication failed")
                return False
        else:
            print_error(f"Bot API returned status {response.status_code}")
            return False
        
        # Test sending message
        print_info("Sending test message...")
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        test_message = "🧪 <b>API Test Successful!</b>\n\n<i>Your AI Agent Briefer is configured correctly.</i>"
        
        data = {
            "chat_id": chat_id,
            "text": test_message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(send_url, data=data, timeout=10)
        
        if response.status_code == 200:
            print_success("Test message sent successfully!")
            print_info("Check your Telegram chat for the test message")
            return True
        else:
            print_error(f"Failed to send message: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Telegram test failed: {str(e)}")
        return False

def test_elevenlabs():
    """Test ElevenLabs API (optional)"""
    print_header("6. Testing ElevenLabs API (Optional)")
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print_warning("ELEVENLABS_API_KEY not set - voice output disabled (optional)")
        return None
    
    try:
        from elevenlabs.client import ElevenLabs
        
        print_info("Initializing ElevenLabs client...")
        client = ElevenLabs(api_key=api_key)
        
        print_info("Testing voice generation (not playing audio)...")
        
        # Generate a very short test audio
        audio = client.generate(
            text="Test",
            voice="Brian",
            model="eleven_multilingual_v2"
        )
        
        # Convert generator to bytes to test
        audio_bytes = b"".join(audio)
        
        if len(audio_bytes) > 0:
            print_success(f"Voice generation successful! ({len(audio_bytes)} bytes)")
            print_success("ElevenLabs API is working! (10k chars/month free tier)")
            return True
        else:
            print_error("Voice generation returned empty audio")
            return False
            
    except Exception as e:
        print_error(f"ElevenLabs test failed: {str(e)}")
        return False

def test_crew_agent():
    """Test a simple CrewAI agent"""
    print_header("7. Testing CrewAI Agent Integration")
    
    try:
        from crewai import Agent, Task, Crew, LLM
        from crewai_tools import SerperDevTool
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print_error("Cannot test agent without GOOGLE_API_KEY")
            return False
        
        print_info("Creating test agent with Gemini 1.5 Flash...")
        
        llm = LLM(
            model="google/gemini-1.5-flash",
            api_key=api_key,
            max_retries=2,
            timeout=60
        )
        
        search_tool = SerperDevTool()
        
        agent = Agent(
            role='Test Analyst',
            goal='Answer a simple test question',
            backstory='A test agent for API validation',
            tools=[search_tool],
            verbose=False,
            llm=llm,
            max_iter=2
        )
        
        task = Task(
            description="What is 2+2? Reply with just the number.",
            expected_output="The number 4",
            agent=agent
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        
        print_info("Running test crew...")
        start_time = time.time()
        
        result = crew.kickoff()
        
        elapsed = time.time() - start_time
        
        print_success(f"Agent completed task in {elapsed:.2f}s")
        print_info(f"Result: {str(result.raw)[:100]}...")
        print_success("CrewAI integration is working!")
        
        return True
        
    except Exception as e:
        print_error(f"CrewAI agent test failed: {str(e)}")
        return False

def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total_tests = len([r for r in results.values() if r is not None])
    passed_tests = len([r for r in results.values() if r is True])
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {Fore.GREEN}{passed_tests}{Style.RESET_ALL}")
    print(f"Failed: {Fore.RED}{total_tests - passed_tests}{Style.RESET_ALL}")
    
    print("\n" + "─" * 70)
    
    if results.get("env") and results.get("gemini_15") and results.get("serper") and results.get("telegram"):
        print_success("All critical tests passed! Your setup is ready. ✨")
        print_info("\nYou can now run: python main.py")
    else:
        print_error("Some critical tests failed. Please fix the issues above.")
        print_info("\nCheck:")
        print_info("1. API keys are set correctly in .env file")
        print_info("2. You have internet connection")
        print_info("3. API quotas are not exceeded")

def main():
    """Run all tests"""
    print(f"{Fore.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║           AI AGENT BRIEFER - API TESTING SUITE                    ║")
    print("║                     100% Free Tier Edition                        ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    results = {}
    
    # Run tests
    results["env"] = test_env_variables()
    
    if results["env"]:
        results["gemini_15"] = test_gemini_15_flash()
        results["gemini_25"] = test_gemini_25_flash()
        results["serper"] = test_serper()
        results["telegram"] = test_telegram()
        results["elevenlabs"] = test_elevenlabs()
        results["crew"] = test_crew_agent()
    else:
        print_error("\nEnvironment variables not set. Skipping API tests.")
        print_info("Create a .env file with required API keys first.")
        sys.exit(1)
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if results.get("gemini_15") and results.get("serper") and results.get("telegram"):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
