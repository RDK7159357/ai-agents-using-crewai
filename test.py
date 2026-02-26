import os
import requests
import json
from dotenv import load_dotenv, find_dotenv

def test_ollama_cloud():

    load_dotenv(find_dotenv())
    # 1. Configuration
    # Use /v1/chat/completions for better 2026 cloud compatibility
    url = "https://ollama.com/api/chat"
    api_key = os.environ.get("OLLAMA_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OLLAMA_API_KEY not found in environment.")
        print("Please run: export OLLAMA_API_KEY='your-key-here'")
        return

    # 2. Setup headers and payload
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-oss:120b-cloud",  # 120B cloud model
        "messages": [
            {"role": "user", "content": "Hello! Are you running on Ollama Cloud?"}
        ],
        "stream": False  # Keeps the response simple for testing
    }

    # 3. Execution
    print(f"Connecting to {url}...")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # Check for auth errors (401) or other issues
        response.raise_for_status()
        
        result = response.json()
        answer = result['message']['content']
        
        print("\n✅ SUCCESS! Cloud Response:")
        print("-" * 30)
        print(answer)
        print("-" * 30)

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP Error: {http_err}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_ollama_cloud()