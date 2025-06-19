# VeoPrompt-Pro: An Agentic Video Prompt Engineering System

VeoPrompt-Pro is a conversational AI agent in Python that guides users through creating detailed, structured, and self-contained prompts for AI video generation models like Google Veo. The system is model-agnostic but optimized for realistic, vlog-style prompt engineering.

## Features
- Multi-turn dialogue for scene elaboration
- Character and setting consistency ("memory")
- Structured data validation with Pydantic
- Realism and style filtering
- Final prompt assembly with Jinja2
- CLI interface with Click and Rich

## Quick Start Guide

### 1. Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up API Keys:**
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"  # Optional, for enhanced realism filtering
   ```

### 2. Launch the UI
```bash
uv run ui.py
```

### 3. Using VeoPrompt-Pro

VeoPrompt-Pro is optimized for creating 8-second VEO3 video prompts. Follow these steps for best results:

1. **Character Description**
   - Focus on upper body and facial features
   - Keep movements simple and natural
   - Example: "A middle-aged man with gentle eyes, slightly graying hair, wearing a casual hiking shirt"

2. **Scene Setting**
   - Describe the immediate environment
   - Include key visual elements
   - Example: "Inside a cozy log cabin, warm firelight casting soft shadows"

3. **Core Action & Dialogue**
   - Keep actions within 8 seconds
   - Use natural speech rates (150-170 words/minute)
   - Example: "He leans forward, speaking softly: 'I've never seen anything like it'"

4. **Camera Style**
   - Prefer medium shots and close-ups
   - Use simple, smooth movements
   - Example: "Medium close-up, slight pan from left to right"

5. **Sounds & Audio**
   - Layer primary and ambient sounds
   - Include precise timing markers
   - Example: "0:00-0:02: Soft crackling fireplace, 0:02-0:05: gentle voice with subtle echo"

6. **Landscape & Props**
   - Focus on elements that enhance the scene
   - Keep details relevant to the 8-second duration
   - Example: "Wooden table with a steaming mug, map spread out nearby"

### 4. Best Practices

1. **Timing Guidelines**
   - Total duration: 8 seconds maximum
   - Dialogue: Keep under 6 seconds
   - Allow 0.5s buffers at start/end

2. **VEO3 Optimization**
   - Avoid complex or rapid movements
   - Focus on facial expressions and upper body
   - Use natural, conversational pacing

3. **Common Pitfalls to Avoid**
   - Overcrowding the 8-second window
   - Complex physical actions
   - Rapid camera movements
   - Overlapping complex sounds

### 5. Example Prompt

```markdown
Character: Middle-aged explorer, weathered face with kind eyes, casual outdoor wear
Action (0-8s):
- 0:00-0:02: Turns to camera, warm smile
- 0:02-0:06: "This discovery changes everything" (spoken naturally)
- 0:06-0:08: Gentle nod, maintaining eye contact
Camera: Medium close-up, stable with subtle zoom
Sounds:
- 0:00-0:08: Soft forest ambience
- 0:02-0:06: Clear voice with natural reverb
```

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
