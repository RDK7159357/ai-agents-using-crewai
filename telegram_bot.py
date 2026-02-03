import os
from dotenv import load_dotenv
import requests
import time
from threading import Thread

load_dotenv()

class TelegramBot:
    def __init__(self, daily_brief_callback, interview_prep_callback):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.daily_brief_callback = daily_brief_callback
        self.interview_prep_callback = interview_prep_callback
        self.last_update_id = 0
        
        if not self.bot_token:
            print("⚠️  TELEGRAM_BOT_TOKEN not set. Bot will not run.")
            return
    
    def send_message(self, text):
        """Send a message to the configured chat"""
        if not self.bot_token or not self.chat_id:
            print("Telegram credentials not set.")
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data)
        except Exception as e:
            print(f"Failed to send message: {e}")
    
    def get_updates(self):
        """Get new messages from Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            return response.json().get("result", [])
        except Exception as e:
            print(f"Error getting updates: {e}")
            return []
    
    def process_message(self, message):
        """Process incoming Telegram message"""
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        
        # Only process messages from the configured chat
        if str(chat_id) != str(self.chat_id):
            return
        
        print(f"📱 Received command: {text}")
        
        if text.startswith("/brief"):
            self.send_message("🚀 Starting daily tech brief...\n<i>This may take a minute.</i>")
            Thread(target=self.daily_brief_callback).start()
        
        elif text.startswith("/interview"):
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                self.send_message("❌ Usage: /interview <company_name>\n\nExample: /interview Google")
            else:
                company = parts[1]
                self.send_message(f"🚀 Starting interview prep for {company}...\n<i>This may take a minute.</i>")
                Thread(target=self.interview_prep_callback, args=(company,)).start()
        
        elif text.startswith("/help") or text == "/start":
            help_text = """<b>🤖 AI Agent Briefer Bot</b>

Available commands:

<b>/brief</b> - Get today's tech news briefing
<b>/interview &lt;company&gt;</b> - Get interview prep for a company
<b>/help</b> - Show this help message

Examples:
• /brief
• /interview Google
• /interview OpenAI"""
            self.send_message(help_text)
        
        else:
            self.send_message("❌ Unknown command. Send /help for available commands.")
    
    def start(self):
        """Start the bot polling loop"""
        if not self.bot_token:
            return
        
        print("🤖 Telegram bot started. Listening for commands...")
        print(f"💬 Chat ID: {self.chat_id}")
        print("\nAvailable commands:")
        print("  /brief - Daily tech briefing")
        print("  /interview <company> - Interview prep")
        print("  /help - Show help\n")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    
                    if "message" in update:
                        self.process_message(update["message"])
                
                time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped.")
                break
            except Exception as e:
                print(f"Error in bot loop: {e}")
                time.sleep(5)
