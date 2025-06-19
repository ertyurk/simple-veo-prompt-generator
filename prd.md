### **Project Title: VeoPrompt-Pro: An Agentic Video Prompt Engineering System**

### **1. Project Overview**

**1.1. Purpose:**
To create a sophisticated, conversational AI agent in Python 3 that guides users through the process of creating detailed, structured, and self-contained prompts for AI video generation models like Google Veo. The system will be model-agnostic at its core but optimized for producing prompts in the realistic, vlog-style format demonstrated in the sample interactions.

**1.2. Core Functionality:**
The system will operate as an interactive **"Prompt Engineering Agent."** Instead of a single transaction, it will engage in a multi-turn dialogue with the user to define, elaborate, and refine scene details. It will manage scene-by-scene construction, enforce consistency for characters and settings, and translate high-level creative ideas into a precise, machine-readable format ready for video generation.

**1.3. Target Audience:**
Content creators, video producers, and marketers who use AI video generation tools and require a streamlined, reliable process for creating high-quality, narrative-driven, and stylistically consistent video content.

---

### **2. System Architecture & Technical Specifications**

**2.1. The Agentic Flow:**
The system is not a simple script but a stateful agent. It works by making multiple calls to AI models to progressively build the final prompt, ensuring all user requirements are met.

1.  **Initial User Input:** The user provides a high-level, conversational request for a scene (e.g., "Bigfoot is in the jungle and catches a weird fish").
2.  **Clarification & Elaboration (Multi-Call Dialogue):** The agent parses the initial input. If details are missing (e.g., mood, specific actions, camera style), it asks clarifying questions. This iterative process continues until it has gathered enough information.
3.  **State Management:** The agent maintains a "memory" of the session, including defined characters, the established environment, and the overall vlog style. This ensures consistency across multiple scenes.
4.  **Structured Data Generation:** Once all details are gathered, the agent structures the information using Pydantic models for validation.
5.  **Realism & Style Validation:** The structured data is passed through a validation filter to ensure it aligns with the desired realistic, "vlog-style" and is not "cartoonish."
6.  **Final Prompt Assembly:** The validated data is formatted into the final, self-contained Markdown prompt using a Jinja2 template.

**2.2. Development Environment:**
* **Language:** Python 3.10 or higher.
* **Package Manager:** UV. Dependencies are managed via `pyproject.toml`.
* **Coding Standards:**
    * **Type Hinting:** Fully type-hinted codebase (non-negotiable).
    * **Formatting & Linting:** Enforced with Black and Ruff.
    * **Modularity:** Well-structured modules (e.g., `agents`, `models`, `templates`, `session_manager`).

**2.3. AI Framework & Model Strategy:**
* **Primary Framework:** **PydanticAI** - Chosen for its model-agnostic support, type-safety, structured response validation, and production-ready features.
* **Model Strategy:**
    * **Primary Model:** **Gemini Models** (for their advanced reasoning, multilingual support for Turkish, and optimization for Google Veo).
    * **Fallback/Specialist Model:** **Anthropic Claude Models** (for superior instruction-following and as a "second opinion" in the realism validation step).

**2.4. Dependencies Architecture:**
```toml
[project]
name = "veoprompt-pro"
version = "1.0.0"
dependencies = [
    "pydantic-ai>=0.3.0",        # Primary AI framework for agentic logic
    "pydantic>=2.0.0",           # Core data modeling and validation
    "click>=8.0.0",              # CLI interface for user interaction
    "rich>=13.0.0",              # Enhanced terminal output and progress indicators
    "jinja2>=3.1.0",             # Template engine for final prompt formatting
]

[project.optional-dependencies]
dev = [
    "black>=23.0.0",             # Code formatting
    "ruff>=0.1.0",               # Linting and style enforcement
    "mypy>=1.7.0",               # Static type checking
    "pytest>=7.0.0",             # Testing framework
]
```

---

### **3. Core Features & Agent Logic**

**3.1. Input Parsing & Elaboration Engine:**
Implemented using a PydanticAI agent, this feature intelligently parses conversational input. If a user states, "Bigfoot is tired of the beatboxing," the agent probes for detail or infers realistic attributes (e.g., "slouched forward," "hands over ears," "visibly exhausted") and validates them against the `SceneInput` model.

**3.2. Character Consistency Engine ("Memory"):**
The system maintains a stateful profile for each character within a session, using Pydantic models for type-safe consistency. This ensures a character defined in Scene 1 maintains its appearance and personality in Scene 4. This engine is generic and can learn new characters on the fly.

**3.3. Scene Construction Module:**
This module uses PydanticAI's structured output capabilities and a Jinja2 template to assemble the final prompt. It dynamically populates the template based on the validated data from the agentic flow, ensuring all required sections are present and correctly formatted.

**3.4. Action & Dialogue Synchronization:**
For timed scenes, the agent breaks down the duration and assigns dialogue and actions to specific timestamps. This is managed with type-safe timing models to ensure logical scene pacing.

**3.5. Realism & Style Filter:**
A key validation step in the agentic flow. This filter checks for "cartoonish" or physically unrealistic elements, grounding the output in the desired vlog style. It can automatically translate a fantastic concept into a realistic execution (e.g., the beatboxing fish sound emanating *from* the fish's location, without the fish's mouth actually syncing).

---

### **4. Data Models & Agent Definitions**

**4.1. Core Pydantic Models:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class CharacterType(str, Enum):
    BIGFOOT = "bigfoot"
    YETI = "yeti"
    BALLOONFISH = "balloonfish"
    CUSTOM = "custom" # Allows for generic character creation

class Character(BaseModel):
    name: str
    character_type: CharacterType
    physical_description: str
    personality_traits: List[str]
    consistency_notes: str = Field(description="Internal notes for maintaining consistency.")

class SceneInput(BaseModel):
    description: str
    characters_in_scene: List[str]
    dialogue: Optional[str] = None
    key_actions: List[str] = Field(default_factory=list)
    duration_seconds: Optional[int] = None
    language: str = "turkish"

class FinalVeoPrompt(BaseModel):
    main_character_description: str
    scene_setting_description: str
    atmosphere_and_mood: str
    core_action_and_dialogue: str
    camera_style: str
    sounds: List[str]
    character_appearance_notes: Dict[str, str]
    landscape_notes: str
    props: List[str]
    timing_breakdown: Optional[Dict[str, str]] = None
```

**4.2. AI Agent Architecture (Conceptual):**
```python
from pydantic_ai import Agent

# Agent to parse user input and ask clarifying questions
input_elaboration_agent = Agent('gemini-1.5-pro', result_type=SceneInput)

# Agent to generate the final prompt structure from validated data
prompt_generator_agent = Agent('gemini-1.5-pro', result_type=FinalVeoPrompt)

# Agent to validate the realism and style of a proposed scene
realism_filter_agent = Agent('claude-3-sonnet', result_type=bool)
```

---

### **5. Generated Prompt Template (Final Output)**

The final output is a self-contained unit generated by populating a Jinja2 template with the `FinalVeoPrompt` model data.

```prompt
Create a realistic, entertaining YouTube vlog video in the style of the channel "Outdoor Boys."

{{ main_character_description }}. He/She is in {{ scene_setting_description }}. The atmosphere is {{ atmosphere_and_mood }}.

The video must look like a genuine, spontaneous moment from a real vlog—not cinematic or overly polished. It should feel natural, handheld, and unfiltered.

{{ core_action_and_dialogue }}

{% if timing_breakdown %}
{% for time, action in timing_breakdown.items() %}
**{{ time }}:** {{ action }}
{% endfor %}
{% endif %}

**Camera style:**
- {{ camera_style }}

**Sounds:**
- {{ sounds | join('\n- ') }}

{% for char, desc in character_appearance_notes.items() %}
**{{ char }} Appearance:**
- {{ desc }}
{% endfor %}

**Landscape:**
- {{ landscape_notes }}

**Props:**
- {{ props | join('\n- ') }}

```

### **6. Implementation Strategy & Success Metrics**

**6.1. Development Phases:**
1.  **Phase 1:** Setup core Pydantic models, UV environment, and basic agent definitions.
2.  **Phase 2:** Implement the Character Consistency Engine and session management (memory).
3.  **Phase 3:** Build the interactive, multi-call Input Elaboration Agent.
4.  **Phase 4:** Develop the Realism Filter and the final Prompt Generation module with Jinja2.
5.  **Phase 5:** Build the user-facing CLI with `click` and `rich`.
6.  **Phase 6:** Comprehensive testing (`pytest`), type checking (`mypy`), and refinement.

**6.2. Success Metrics:**
* **Technical:** 100% type hint coverage; Zero `mypy` errors; Low-latency agent responses.
* **Functional:** High degree of character/style consistency across scenes; Accurate preservation of specified language (Turkish); High user satisfaction with the quality and realism of the generated prompts.