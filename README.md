# LangGraph Web Research Agent

This is a multi-agent AI system for automated web research, built with LangGraph, LangChain, and Python.

## Features

- **Search Agent**: Aggregates results from Web (Tavily) and YouTube.
- **Content Extractor**: Scrapes web pages and fetches YouTube transcripts.
- **Summarization Agent**: Summarizes content using LLM.
- **Analyzer Agent**: Analyzes trends and sentiment.
- **Report Generator**: Produces a Markdown report.

## Setup

1. **Install Dependencies**:
   ```bash
   uv sync
   # or
   pip install -r pyproject.toml
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Required Keys:
   - `OPENAI_API_KEY`: For Summarization and Analysis.
   - `TAVILY_API_KEY`: For Web Search.
   - `YOUTUBE_API_KEY`: For YouTube Search (Optional, uses Google Cloud Console).

## Usage

Run the agent with a query:

```bash
uv run python -m src.main "Your Research Topic"
```

Example:
```bash
uv run python -m src.main "Generative AI Trends 2025"
```

## Structure

- `src/agents/`: Individual agent logic.
- `src/graph.py`: LangGraph state machine definition.
- `src/state.py`: Shared state schema.
- `src/utils/`: Helper tools (Search, Scraping, LLM).
