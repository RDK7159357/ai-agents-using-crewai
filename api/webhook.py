# Vercel Serverless Function for Telegram Webhook
import json
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
        requests.post(url, data=data, timeout=10)
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
        response = requests.post(url, json=data, headers=headers, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"Error triggering workflow: {e}")
        return False

def handler(request):
    """Vercel serverless function handler"""
    try:
        if request.method == 'GET':
            return {"statusCode": 200, "body": json.dumps({"message": "Webhook is running"})}
        
        if request.method != 'POST':
            return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}
        
        # Parse the request body
        body = request.get_json() if hasattr(request, 'get_json') else json.loads(request.body)
        
        if 'message' not in body:
            return {"statusCode": 200, "body": json.dumps({"ok": True})}
        
        message = body['message']
        chat_id = str(message.get('chat', {}).get('id'))
        text = message.get('text', '')
        
        # Only process messages from the configured chat
        if chat_id != str(TELEGRAM_CHAT_ID):
            return {"statusCode": 200, "body": json.dumps({"ok": True})}
        
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

<b>/brief</b> - Daily tech news briefing
<b>/interview &lt;company&gt;</b> - Interview prep for a company
<b>/help</b> - Show this help message

Examples:
• /brief
• /interview Google

<i>Serverless on Vercel + GitHub Actions!</i>"""
            send_telegram_message(help_text)
        
        return {"statusCode": 200, "body": json.dumps({"ok": True})}
    
    except Exception as e:
        print(f"Error in webhook handler: {e}")
        import traceback
        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps({"ok": False, "error": str(e)})}
