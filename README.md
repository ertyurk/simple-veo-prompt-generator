# VeoPrompt-Pro: An Agentic Video Prompt Engineering System

VeoPrompt-Pro is a conversational AI agent in Python that guides users through creating detailed, structured, and self-contained prompts for AI video generation models like Google Veo. The system is model-agnostic but optimized for realistic, vlog-style prompt engineering.

## Features
- Multi-turn dialogue for scene elaboration
- Character and setting consistency ("memory")
- Structured data validation with Pydantic
- Realism and style filtering
- Final prompt assembly with Jinja2
- CLI interface with Click and Rich

## Development Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```
2. **Run scripts:**
   ```bash
   uv run <script.py>
   ```
3. **Add dependencies:**
   ```bash
   uv add <package>
   ```
4. **Dev tools:**
   ```bash
   uv sync --dev
   uv run -m black .
   uv run -m ruff .
   uv run -m mypy .
   uv run -m pytest
   ```

## Project Structure
- `agents/` — Agent logic and orchestration
- `models/` — Pydantic models for scenes, characters, prompts
- `templates/` — Jinja2 templates for prompt formatting
- `session_manager/` — State and memory management
- `cli.py` — CLI entry point

See `prd.md` for full product requirements and architecture.
