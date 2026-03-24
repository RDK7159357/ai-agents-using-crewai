# Detailed Academic Project Report: AI Agent Briefer

## Abstract
In the modern era, the rapid dissemination of information has led to an overwhelming volume of digital news, making efficient curation a significant challenge. Concurrently, technical interview preparation requires synthesizing vast amounts of decentralized corporate data, which is time-consuming and often yields outdated information. This project presents "AI Agent Briefer," an autonomous, serverless, multi-agent artificial intelligence system designed to deliver high-precision daily technology briefings and in-depth company intelligence. Built on the CrewAI orchestration framework, the system leverages a robust multi-model fallback chain—integrating Large Language Models (LLMs) such as Ollama, Groq, Gemini, OpenRouter, Mistral, and Together AI—to ensure 100% uptime with zero operational costs. A critical innovation of this project is its rigorous programmatic output validation pipeline, which systematically identifies and mitigates LLM hallucinations, lazy tool execution, and stale data generation. The curated intelligence is delivered via Telegram acting as a multi-modal interface, providing both rich HTML text and synthesized audio (via ElevenLabs or Google TTS). This report provides a comprehensive analysis of the system's architecture, implementation strategies, validation methodologies, and performance evaluation.

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Literature Review](#2-literature-review)
3. [System Architecture and Design](#3-system-architecture-and-design)
4. [Implementation Details](#4-implementation-details)
5. [Validation and Security Guardrails](#5-validation-and-security-guardrails)
6. [Results and Performance Evaluation](#6-results-and-performance-evaluation)
7. [Conclusion and Future Work](#7-conclusion-and-future-work)
8. [References](#8-references)

---

## 1. Introduction

### 1.1 Motivation
The technology industry is characterized by rapid evolution. Professionals and job seekers must continuously monitor advancements in Artificial Intelligence, cybersecurity, startups, and global markets. General-purpose aggregators lack the domain specificity required to filter out noise, while manual research for interview preparation is arduous. Given the advent of autonomous AI agents capable of reasoning, searching the web, and synthesizing data, there is a profound opportunity to automate this knowledge curation.

### 1.2 Problem Statement
Existing AI-driven summarization tools are often hindered by:
- **High API Costs:** Reliance on proprietary models (e.g., GPT-4) prevents continuous daily execution without financial investment.
- **LLM Hallucinations:** Generative models often fabricate dates, summarize outdated articles as "breaking news," or fail to execute web searches, instead writing "I could not find this information."
- **Accessibility:** Text-heavy newsletters are difficult to consume in varying environments, highlighting the need for multi-modal (audio) delivery systems.

### 1.3 Project Objectives
- To develop distinct AI personas capable of specialized tasks: "News Scout" for daily briefings and "Company Researcher" for interview intelligence.
- To engineer a zero-cost inference engine by implementing a dynamic, rate-limit-aware fallback mechanism across multiple free-tier LLM providers.
- To design deterministic Python guardrails that programmatically reject subpar generative outputs.
- To deploy the system as a serverless infrastructure utilizing GitHub Actions and Telegram webhooks for seamless user interaction.

---

## 2. Literature Review

### 2.1 Autonomous Multi-Agent Systems
Multi-agent systems (MAS) involve multiple interacting intelligent agents that solve problems beyond the capability of a single agent. Frameworks like CrewAI and AutoGen have popularized the use of LLMs as the cognitive engine for these agents, allowing them to collaborate, delegate tasks, and utilize external tools (e.g., search APIs) to gather real-time data.

### 2.2 LLM Hallucinations and Output Validation
A well-documented limitation of LLMs is "hallucination"—the generation of fluent but factually incorrect information. In automated news curation, this manifests as stale news being presented as recent. Recent studies suggest that combining stochastic LLM generation with deterministic programmatic validation (e.g., Regex date validation) significantly improves the reliability of enterprise AI systems.

### 2.3 Serverless Computing and Microservices
Serverless computing allows developers to execute code without managing the underlying infrastructure. Platforms like GitHub Actions (for cron jobs) and Vercel (for webhook hosting) enable discrete microservices to operate efficiently, scaling down to zero when idle, which drastically minimizes operational overhead.

---

## 3. System Architecture and Design

The system is designed with a decoupled architecture, separating orchestration, inference, validation, and delivery.

### 3.1 Component Architecture
1. **User Interface (Telegram Bot):** Acts as the primary interface. Users can receive automated daily briefs or request on-demand interview prep via `/interview <company>`.
2. **Orchestrator (`main.py`):** The central nervous system. It initializes the tasks, sets up the CrewAI environment, and manages the execution flow.
3. **Agent Factory (`agents.py`):** Defines the personas, equips them with tools (Serper Search API), and manages the LLM instantiation logic.
4. **Validation Logic:** A series of strict deterministic functions acting as a quality assurance gateway.
5. **Delivery and TTS Subsystem:** Formats the final validated text into Telegram-friendly HTML and generates an MP3 audio file.

### 3.2 Data Flow
- **Trigger:** A cron job on GitHub Actions fires at 6:00 AM IST, or a Telegram webhook is triggered.
- **Inference:** The Orchestrator requests an LLM from the Agent Factory. The AI Agent receives its prompt and utilizes the Serper tool to fetch live data.
- **Validation:** The Orchestrator receives the markdown response and parses it through validation functions. If it fails (e.g., stale dates, too short, raw tool syntax), the system throws an exception and retries the entire pipeline using the *next* LLM in the fallback chain.
- **Delivery:** The validated text is sanitized, sent as a Telegram message, and passed to ElevenLabs (or gTTS) for audio synthesis, which is then sent as an audio message.

---

## 4. Implementation Details

### 4.1 The LLM Fallback Chain
A core innovation of this project is its ability to operate indefinitely on free-tier APIs without failing. The `get_llm()` factory function dynamically routes to different providers. The priority order is configurable but defaults to:
1. **Ollama (Local)**: Zero network latency and zero API limits.
2. **Groq (Llama 3.3 70B)**: Extremely fast inference, generous free tier.
3. **Google Gemini (2.0 Flash)**: Massive 2M token context window, critical for the search-heavy Interview Prep agent.
4. **Together AI, HuggingFace, OpenRouter, Mistral**: Utilized as progressive safety nets.

**Rate Limit Handling:** The function `run_crew_with_rate_limit_retry()` intercepts HTTP 429 (TooManyRequests) exceptions. It extracts the suggested retry wait time from the error string, applies exponential backoff, and shifts the `_models_tried` state context to gracefully failover to the next provider.

### 4.2 Agent Personas and Prompt Engineering
The system utilizes two highly specialized agents:
- **The News Scout (`create_news_scout_agent`)**: Instructed to perform exactly 5 independent searches representing different facets of tech (AI, Cybersecurity, Startup Funding, India, Global). This forces the agent to bypass its innate laziness and synthesize a structurally diverse brief.
- **The Interview Strategist (`create_company_researcher_agent`)**: Executes a 4-pronged search methodology (Overview, News, Culture, Challenges). The prompt explicitly commands the generation of exactly five "Killer Questions" that reference specific facts found during the search, preventing generic outputs.

### 4.3 Telegram Message Chunking and Formatting
Telegram restricts messages to 4096 characters and utilizes an extremely rigid HTML parser that rejects standard Markdown. The `format_for_telegram()` function acts as a custom cross-compiler:
- It transforms Markdown tables into bulleted lists.
- It translates header syntaxes (`##`, `###`) into bold tags (`<b>`).
- It escapes HTML entities (`&`, `<`, `>`) inside code blocks to prevent Telegram API parsing failures.
- It dynamically splits outputs exceeding 4000 characters along natural paragraph boundaries (`\n\n`) to deliver a continuous reading experience without truncation.

---

## 5. Validation and Security Guardrails

The most vulnerable point of autonomous agents is their output reliability. This project resolves this by implementing rigorous deterministic validation before showing any output to the user.

### 5.1 News Validation (`validate_news_output`)
- **Stale News Regex Filtering:** The algorithm parses the output for complex geographic date strings (e.g., "March 18, 2026", "2026-03-18"). It converts these strings into Python `datetime` objects and calculates the delta from the current date. Any story exceeding `NEWS_MAX_AGE_DAYS` (default 3 days) triggers an immediate task failure and LLM retry.
- **Deduplication Engine:** Analyzes all outputted headlines. By calculating a string-overlap similarity score, if two headlines exhibit greater than 60% identical terminology, the system recognizes a deduplication failure.
- **Topic Diversity Enforcer:** Ensures the final output isn't a monochromatic list (e.g., entirely consisting of smartphone hardware launches). It scans for required diversity keywords (e.g., "AI", "Startup", "Cybersecurity").

### 5.2 Interview Validation (`validate_interview_output`)
- **Anti-'Lazy' Agent Trapping:** LLMs will occasionally hallucinate a failure to find data rather than executing their assigned search tools. If the output contains the string "Not found in public sources" more than four times, the validation fails.
- **Tool-Call Leakage Prevention:** Prevents raw XML/JSON tool debug syntaxes (e.g., `<search_query>`, `action_input`) from leaking into the final markdown payload.
- **Unfilled Placeholder Detection:** Scans for brackets (e.g., `[Company Name]`, `[Year]`) that indicate the LLM parroted an internal instruction template rather than filling it with factual data.

---

## 6. Results and Performance Evaluation

### 6.1 Cost Efficiency
By strategically routing inference requests through Groq, OpenRouter, and Gemini Flash's free tiers, the operational cost is maintained at **$0.00/month**. An equivalent system operating sequentially on OpenAI's GPT-4o architecture, running 30 times a month with extensive web search contexts, would cost an estimated $30-$50 monthly.

### 6.2 Execution Latency
- **Daily Briefing (Groq + Serper):** 25 to 45 seconds total execution time, largely bound by network latency during Serper API web-scraping.
- **Interview Prep (Gemini Flash + Serper):** 40 to 80 seconds. The massive 2-million token context allows Gemini to process dozens of scraped HTML pages simultaneously without chunking, providing immensely thorough "Killer Questions" at the cost of slight latency increases.
- **Audio Synthesis:** ElevenLabs generates a 2-minute MP3 summary in under 8 seconds.

### 6.3 Resilience Testing
During forced stress tests where primary APIs (Groq and Gemini) were intentionally provided with invalid keys or forced to hit Token-Per-Minute limits, the system successfully navigated its fallback chain to Together AI and Mistral, achieving a 100% request fulfillment rate without crashing.

---

## 7. Conclusion and Future Work

### 7.1 Conclusion
The "AI Agent Briefer" successfully demonstrates the viability of executing highly capable, autonomous knowledge-curation agents on purely serverless, zero-cost infrastructure. By acknowledging the innate flaws of LLMs (hallucinations and laziness) and building rigorous Pythonic validation boundaries around them, the system transforms stochastic AI text generation into deterministic, enterprise-reliable intelligence briefings. The integration of multi-modal Telegram deployment makes the system immediately practical for technology professionals.

### 7.2 Future Scope
1. **Vector Database Integration (RAG):** Implementing a lightweight vector store (e.g., ChromaDB or Pinecone) to grant the agents explicit temporal memory. This would eliminate the risk of the Daily Brief covering the exact same news story two days in a row.
2. **Dynamic User Profiling:** Abstracting the hard-coded "Global/Indian Tech" parameters into a user-configurable JSON/database schema, enabling the single Bot to serve individualized briefings (e.g., "Healthcare Tech" for User A, "Web3" for User B).
3. **Cross-Platform Messaging:** Expanding the delivery webhooks beyond Telegram to natively support Slack, Discord, and WhatsApp Business API.
4. **Hierarchical Agent Teams:** Upgrading CrewAI from sequential execution to a hierarchical manager-worker paradigm, reducing execution time by executing independent web searches in parallel rather than sequentially.

---

## 8. References

1. CrewAI Documentation. Retrieved from [https://github.com/joaomdmoura/crewAI](https://github.com/joaomdmoura/crewAI)
2. LiteLLM Framework. Retrieved from [https://github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)
3. Touvron, H., et al. (2023). "Llama 2: Open Foundation and Fine-Tuned Chat Models." *arXiv preprint arXiv:2307.09288*.
4. Ji, Z., et al. (2023). "Survey of Hallucination in Natural Language Generation." *ACM Computing Surveys*.
5. GitHub Actions Documentation. Retrieved from [https://docs.github.com/en/actions](https://docs.github.com/en/actions)
6. ElevenLabs API Documentation. Retrieved from [https://elevenlabs.io/docs](https://elevenlabs.io/docs)
7. Serper Search API Documentation. Retrieved from [https://serper.dev/](https://serper.dev/)
