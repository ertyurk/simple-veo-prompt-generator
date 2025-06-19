from pydantic_ai import Agent
from models import SceneInput, FinalVeoPrompt
from config import Config

# Check if API keys are available
google_key = Config.get_google_api_key()
anthropic_key = Config.get_anthropic_api_key()

# Agent to parse user input and ask clarifying questions
if google_key:
    input_elaboration_agent = Agent(
        model="gemini-2.5-flash",
        output_type=SceneInput,
    )
    prompt_generator_agent = Agent(
        model="gemini-2.5-flash",
        output_type=FinalVeoPrompt,
    )
else:
    input_elaboration_agent = None
    prompt_generator_agent = None

# Agent to validate the realism and style of a proposed scene
if anthropic_key:
    realism_filter_agent = Agent(
        model="claude-3-5-haiku-latest",
        output_type=bool,
    )
else:
    realism_filter_agent = None