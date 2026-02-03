# Setup Telegram Webhook

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = input("Enter your webhook URL (e.g., https://your-app.vercel.app/webhook): ")

# Set webhook
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
data = {"url": WEBHOOK_URL}

response = requests.post(url, json=data)
print(response.json())

if response.json().get("ok"):
    print(f"✅ Webhook set successfully to: {WEBHOOK_URL}")
else:
    print("❌ Failed to set webhook")

# Check webhook info
info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
info_response = requests.get(info_url)
print("\nWebhook Info:")
print(info_response.json())
