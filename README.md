# AI Agent Briefer

An AI-powered briefing system that uses CrewAI agents to deliver news summaries and interview preparation insights.

## Features

- **Daily Brief**: Summarizes the top 3 AI breakthroughs from the last 24 hours with text-to-speech
- **Interview Prep**: Research companies and generate 5 talking points for interviews

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   SERPER_API_KEY=your_serper_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   GEMINI_API_KEY=your_gemini_key (optional)
   ```

## Usage

```python
from main import daily_brief, interview_prep

# Get daily AI news briefing
daily_brief()

# Get interview prep for a company
interview_prep("OpenAI")
```

## API Keys

- **Serper**: [https://serper.dev](https://serper.dev) - For web search
- **ElevenLabs**: [https://elevenlabs.io](https://elevenlabs.io) - For text-to-speech
- **Gemini** (optional): [https://ai.google.dev](https://ai.google.dev) - For additional AI features

## License

MIT
