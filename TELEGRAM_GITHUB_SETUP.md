# Telegram Bot GitHub Integration Setup

This guide will help you set up your Telegram bot to trigger GitHub Actions workflows.

## Prerequisites

1. A GitHub repository with this code
2. A Telegram bot (already created with BotFather)
3. GitHub Personal Access Token

## Step 1: Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Or visit: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name like "Telegram Bot Workflow Trigger"
4. Set expiration (recommend: 90 days or No expiration)
5. Select these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
6. Click "Generate token"
7. **Copy the token immediately** (you won't see it again!)

## Step 2: Update .env File

Add these two variables to your `.env` file:

```bash
# Telegram Bot Configuration (already configured)
TELEGRAM_BOT_TOKEN=your_existing_bot_token
TELEGRAM_CHAT_ID=your_existing_chat_id

# GitHub Integration (NEW - add these)
GITHUB_TOKEN=ghp_your_personal_access_token_here
GITHUB_REPO=yourusername/yourreponame

# Example:
# GITHUB_REPO=ramadugudhanush/ai-agent-briefer
```

## Step 3: Update GitHub Secrets

Your GitHub Actions workflow needs these secrets. Add them in your repository:

1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret" for each:

- `GOOGLE_API_KEY`
- `GROQ_API_KEY`
- `OPENROUTER_API_KEY`
- `MISTRAL_API_KEY`
- `SERPER_API_KEY`
- `ELEVENLABS_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `PREFERRED_MODEL` (optional)

## Step 4: Check Your Default Branch Name

The bot defaults to triggering workflows on the `main` branch. If your default branch is different:

1. Check your default branch:
   ```bash
   git branch --show-current
   ```

2. If it's not `main` (e.g., it's `master`), edit `telegram_bot_github.py`:
   ```python
   data = {
       "ref": "master",  # Change from "main" to your branch name
       "inputs": inputs or {}
   }
   ```

## Step 5: Run the Telegram Bot

Start the GitHub-integrated bot:

```bash
python telegram_bot_github.py
```

## Available Commands

Once running, you can use these commands in Telegram:

- `/brief` - Trigger daily tech briefing workflow
- `/interview Google` - Trigger interview prep workflow for Google
- `/help` - Show help message

## How It Works

1. You send a command in Telegram (e.g., `/brief`)
2. The bot receives the command
3. Bot calls GitHub API to trigger the workflow
4. GitHub Actions runs the workflow in the cloud
5. Workflow executes your Python scripts
6. Results are sent to your Telegram chat

## Troubleshooting

### "Failed to trigger workflow. Status: 404"
- Check that `GITHUB_REPO` is in format `username/repo`
- Verify the workflow file is named `briefer.yml` in `.github/workflows/`

### "Failed to trigger workflow. Status: 403"
- GitHub token doesn't have correct permissions
- Create new token with `repo` and `workflow` scopes

### "Failed to trigger workflow. Status: 422"
- Check that your default branch name is correct
- Verify the workflow has `workflow_dispatch` trigger

### Bot doesn't respond
- Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct
- Make sure you're messaging from the correct chat

## Testing

1. Start the bot: `python telegram_bot_github.py`
2. Send `/brief` in Telegram
3. Check GitHub Actions tab in your repository to see if workflow started
4. Wait 2-3 minutes for results in Telegram

## Comparison: Local vs GitHub Actions

### `telegram_bot.py` (Local Execution)
- Runs scripts on your computer
- Faster (no GitHub Actions startup time)
- Requires computer to be running
- Use for development/testing

### `telegram_bot_github.py` (Cloud Execution)
- Runs on GitHub's servers
- Works even when your computer is off
- Takes 2-3 minutes (GitHub Actions startup)
- Better for production/scheduled tasks

Choose the one that fits your needs!
