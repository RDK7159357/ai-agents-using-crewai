# Vercel Serverless Function for Telegram Webhook
import json
import os
import requests
from http.server import BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

def send_telegram_message(text):
    """Send a message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
        print(f"✅ Telegram message sent")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

def trigger_workflow_dispatch(workflow_id, inputs=None):
    """Trigger GitHub Actions workflow"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{workflow_id}/dispatches"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {
            "ref": "main",
            "inputs": inputs or {}
        }
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"GitHub response: {response.status_code}")
        return response.status_code == 204
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    """Vercel handler for Telegram webhook"""
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            print(f"📨 Received webhook: {data}")
            
            if 'message' not in data:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
                return
            
            message = data['message']
            chat_id = str(message.get('chat', {}).get('id'))
            text = message.get('text', '')
            
            print(f"Chat ID: {chat_id}, Text: {text}")
            
            # Only process from our chat
            if chat_id != str(TELEGRAM_CHAT_ID):
                print(f"❌ Chat ID mismatch: {chat_id} != {TELEGRAM_CHAT_ID}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
                return
            
            print(f"📱 Processing command: {text}")
            
            if text.startswith('/brief'):
                send_telegram_message("🚀 Triggering daily tech brief...\n<i>This may take 2-3 minutes.</i>")
                trigger_workflow_dispatch("briefer.yml", {"mode": "daily"})
            
            elif text.startswith('/interview'):
                parts = text.split(maxsplit=1)
                if len(parts) < 2:
                    send_telegram_message("❌ Usage: /interview <company_name>\n\nExample: /interview Google")
                else:
                    company = parts[1]
                    send_telegram_message(f"🚀 Triggering interview prep for {company}...\n<i>This may take 2-3 minutes.</i>")
                    trigger_workflow_dispatch("briefer.yml", {"mode": "interview", "company": company})
            
            elif text.startswith('/help') or text == '/start':
                help_text = """<b>🤖 AI Agent Briefer Bot</b>

<b>/brief</b> - Daily tech news briefing
<b>/interview &lt;company&gt;</b> - Interview prep for a company
<b>/help</b> - Show this help message

Examples:
• /brief
• /interview Google

<i>Serverless on Vercel + GitHub Actions!</i>"""
                send_telegram_message(help_text)
            
            else:
                send_telegram_message("❌ Unknown command. Send /help for available commands.")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        
        except Exception as e:
            print(f"❌ Error in webhook: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Telegram webhook is running"}).encode())
    
    def log_message(self, format, *args):
        """Override to log messages"""
        print(f"[{self.client_address[0]}] {format % args}")
