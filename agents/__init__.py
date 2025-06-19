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
        system_prompt="""You are a video production analyst specializing in realistic vlog-style content. Parse user inputs and extract structured scene information.

Focus on realistic, observable actions. Avoid cartoonish or fantastical elements. Think like a real vlogger capturing genuine moments."""
    )

    final_assembly_agent = Agent(
        model="gemini-2.5-flash",
        output_type=FinalVeoPrompt,
        system_prompt="""You are a video prompt engineer creating realistic vlog-style prompts for VEO3 video generation.

CRITICAL: Every element must be physically realistic and natural. Avoid cartoonish expressions, movements, or behaviors. Create prompts that feel like genuine, spontaneous vlog moments.

Focus on facial expressions and upper body movements within 8 seconds. Use realistic camera angles and natural dialogue."""
    )

    # Specialized enrichment agents
    character_enrichment_agent = Agent(
        model="gemini-2.5-flash",
        output_type=str,
        system_prompt="""You are a VEO3 character optimization specialist. Enhance character descriptions for realistic video generation.

Focus on realistic facial features and expressions. Avoid exaggerated or cartoonish descriptions. Think in terms of real people, not animated characters.

Optimize for VEO3's strengths: natural skin textures, realistic hair/clothing, authentic facial expressions."""
    )

    camera_enrichment_agent = Agent(
        model="gemini-2.5-flash",
        output_type=str,
        system_prompt="""You are a VEO3 camera movement specialist. Create realistic camera instructions for authentic vlog-style video.

Use natural, handheld camera movements. Avoid cinematic or overly polished work. Think like a real person holding a camera.

Prefer stable positions with subtle movements VEO3 handles well."""
    )

    sounds_enrichment_agent = Agent(
        model="gemini-2.5-flash",
        output_type=str,
        system_prompt="""You are a VEO3 sound design specialist. Create realistic audio descriptions for authentic vlog-style video.

Use natural, realistic sounds and dialogue. Avoid cartoonish or exaggerated audio elements. Think like real audio from genuine vlog footage.

Focus on natural speech rates, realistic ambient sounds, and authentic dialogue delivery."""
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
        system_prompt="""You are a realism validator for AI video generation. Determine if a scene will produce realistic, non-cartoonish video content.

REJECT if contains: exaggerated expressions, cartoonish elements, unrealistic actions, overly dramatic elements, or anything artificial.

APPROVE only if: realistic, physically possible, authentic, suitable for vlog-style video, and free from cartoonish elements.

Return TRUE for realistic scenes, FALSE for cartoonish content."""
    )
else:
    realism_filter_agent = None