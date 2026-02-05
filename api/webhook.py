# Vercel Serverless Function for Telegram Webhook
from flask import request, jsonify
import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send message: {e}")

def trigger_workflow_dispatch(workflow_id, inputs=None):
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

def handler(request):
    """Vercel serverless function handler"""
    if request.method != 'POST':
        return jsonify({"error": "Method not allowed"}), 405
    
    try:
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({"ok": True})
        
        message = data['message']
        chat_id = str(message.get('chat', {}).get('id'))
        text = message.get('text', '')
        
        if chat_id != TELEGRAM_CHAT_ID:
            return jsonify({"ok": True})
        
        if text.startswith('/brief'):
            send_telegram_message("🚀 Triggering daily tech brief...\n<i>This may take 2-3 minutes.</i>")
            trigger_workflow_dispatch("briefer.yml", {"mode": "daily"})
        
        elif text.startswith('/interview'):
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                send_telegram_message("❌ Usage: /interview <company_name>")
            else:
                company = parts[1]
                send_telegram_message(f"🚀 Triggering interview prep for {company}...")
                trigger_workflow_dispatch("briefer.yml", {"mode": "interview", "company": company})
        
        elif text.startswith('/help') or text == '/start':
            help_text = """<b>🤖 AI Agent Briefer Bot</b>

<b>/brief</b> - Daily tech news
<b>/interview &lt;company&gt;</b> - Interview prep
<b>/help</b> - Show help

<i>Serverless on Vercel + GitHub Actions!</i>"""
            send_telegram_message(help_text)
        
        return jsonify({"ok": True})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"ok": False}), 500
