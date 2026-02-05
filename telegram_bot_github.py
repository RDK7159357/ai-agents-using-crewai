import os
from dotenv import load_dotenv
import requests
import time
from threading import Thread

load_dotenv()

class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO")  # Format: "username/repo"
        self.last_update_id = 0
        
        if not self.bot_token:
            print("⚠️  TELEGRAM_BOT_TOKEN not set. Bot will not run.")
            return
        
        if not self.github_token or not self.github_repo:
            print("⚠️  GITHUB_TOKEN or GITHUB_REPO not set. GitHub Actions won't work.")
    
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
    
    def trigger_workflow_dispatch(self, workflow_id, inputs=None):
        """Trigger a GitHub Actions workflow via workflow_dispatch"""
        if not self.github_token or not self.github_repo:
            self.send_message("❌ GitHub integration not configured. Please set GITHUB_TOKEN and GITHUB_REPO.")
            return
        
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/actions/workflows/{workflow_id}/dispatches"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {self.github_token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {
                "ref": "main",  # or "master" depending on your default branch
                "inputs": inputs or {}
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 204:
                print(f"✅ Triggered workflow: {workflow_id}")
                return True
            else:
                print(f"❌ Failed to trigger workflow: {response.status_code} - {response.text}")
                self.send_message(f"❌ Failed to trigger workflow. Status: {response.status_code}\n{response.text}")
                return False
                
        except Exception as e:
            print(f"Error triggering GitHub Action: {e}")
            self.send_message(f"❌ Error: {e}")
            return False
    
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
            self.send_message("🚀 Triggering daily tech brief on GitHub Actions...\n<i>This may take 2-3 minutes.</i>")
            self.trigger_workflow_dispatch("briefer.yml", {"mode": "daily"})
        
        elif text.startswith("/interview"):
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                self.send_message("❌ Usage: /interview <company_name>\n\nExample: /interview Google")
            else:
                company = parts[1]
                self.send_message(f"🚀 Triggering interview prep for {company} on GitHub Actions...\n<i>This may take 2-3 minutes.</i>")
                self.trigger_workflow_dispatch("briefer.yml", {"mode": "interview", "company": company})
        
        elif text.startswith("/help") or text == "/start":
            help_text = """<b>🤖 AI Agent Briefer Bot</b>

Available commands:

<b>/brief</b> - Get today's tech news briefing
<b>/interview &lt;company&gt;</b> - Get interview prep for a company
<b>/help</b> - Show this help message

Examples:
• /brief
• /interview Google
• /interview OpenAI

<i>Note: Commands trigger GitHub Actions workflows that run in the cloud.</i>"""
            self.send_message(help_text)
        
        else:
            self.send_message("❌ Unknown command. Send /help for available commands.")
    
    def start(self):
        """Start the bot polling loop"""
        if not self.bot_token:
            return
        
        print("🤖 Telegram bot started. Listening for commands...")
        print(f"💬 Chat ID: {self.chat_id}")
        print(f"🔧 GitHub Repo: {self.github_repo}")
        print("\nAvailable commands:")
        print("  /brief - Daily tech briefing (triggers GitHub Action)")
        print("  /interview <company> - Interview prep (triggers GitHub Action)")
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

if __name__ == "__main__":
    bot = TelegramBot()
    bot.start()
