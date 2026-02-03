import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Testing Gemini API key...")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")

# List available models
print("\nAvailable Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")

# Try a simple generation
print("\nTesting simple generation with gemini-1.5-flash...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello!")
    print(f"✅ Success: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
