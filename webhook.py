import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

def send_telegram_message(text):
    """Send a message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send message: {e}")

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
        
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 204
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram webhook"""
    try:
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({"ok": True})
        
        message = data['message']
        chat_id = str(message.get('chat', {}).get('id'))
        text = message.get('text', '')
        
        # Only process messages from the configured chat
        if chat_id != TELEGRAM_CHAT_ID:
            return jsonify({"ok": True})
        
        print(f"📱 Received: {text}")
        
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

Available commands:

<b>/brief</b> - Get today's tech news briefing
<b>/interview &lt;company&gt;</b> - Get interview prep for a company
<b>/help</b> - Show this help message

Examples:
• /brief
• /interview Google
• /interview OpenAI

<i>Runs on serverless GitHub Actions!</i>"""
            send_telegram_message(help_text)
        
        else:
            send_telegram_message("❌ Unknown command. Send /help for available commands.")
        
        return jsonify({"ok": True})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/')
def home():
    return "Telegram Bot Webhook is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
