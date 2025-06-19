from pydantic_ai import Agent
from models import SceneInput, FinalVeoPrompt
from config import Config

# Check if API keys are available
google_key = Config.get_google_api_key()
anthropic_key = Config.get_anthropic_api_key()

# Core agents for context and assembly
if google_key:
    context_analysis_agent = Agent(
        model="gemini-2.5-flash",
        output_type=SceneInput,
    )

    final_assembly_agent = Agent(
        model="gemini-2.5-flash",
        output_type=FinalVeoPrompt,
    )

    # Specialized enrichment agents
    character_enrichment_agent = Agent(
        model="gemini-2.5-flash",
        output_type=str,
    )

    camera_enrichment_agent = Agent(
        model="gemini-2.5-flash",
        output_type=str,
    )

    sounds_enrichment_agent = Agent(
        model="gemini-2.5-flash",
        output_type=str,
    )
else:
    context_analysis_agent = None
    final_assembly_agent = None
    character_enrichment_agent = None
    camera_enrichment_agent = None
    sounds_enrichment_agent = None

# Agent to validate the realism and style of a proposed scene
if anthropic_key:
    realism_filter_agent = Agent(
        model="claude-3-5-haiku-latest",
        output_type=bool,
    )
else:
    realism_filter_agent = None