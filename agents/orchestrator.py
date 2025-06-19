from typing import Any
from models import SceneInput, FinalVeoPrompt, Character
from session_manager import SessionManager
from agents import input_elaboration_agent, prompt_generator_agent, realism_filter_agent
from config import Config

class Orchestrator:
    def __init__(self, session: SessionManager) -> None:
        self.session = session
        # Validate API keys on initialization
        Config.validate_api_keys()

    def process_user_input(self, user_input: str) -> FinalVeoPrompt:
        # Check if agents are available
        if not input_elaboration_agent:
            raise RuntimeError("Google API key not set. Cannot process input.")

        # Step 1: Elaborate input
        result = input_elaboration_agent.run_sync(user_input)
        scene: SceneInput = result.output
        self.session.add_scene(scene)

        # Step 2: Update character memory
        for char_name in scene.characters_in_scene:
            if not self.session.get_character(char_name):
                # In a real system, you'd elaborate character details here
                self.session.add_character(Character(
                    name=char_name,
                    character_type="custom",
                    physical_description="",
                    personality_traits=[],
                    consistency_notes=""
                ))

        # Step 3: Realism/style validation (skip if agent not available)
        if realism_filter_agent:
            realism_result = realism_filter_agent.run_sync(str(scene))
            is_realistic: bool = realism_result.output
            if not is_realistic:
                raise ValueError("Scene failed realism/style validation.")
        else:
            print("Warning: Skipping realism validation (Anthropic API key not set).")

        # Step 4: Generate final prompt
        if not prompt_generator_agent:
            raise RuntimeError("Google API key not set. Cannot generate prompt.")

        prompt_result = prompt_generator_agent.run_sync(str(scene))
        final_prompt: FinalVeoPrompt = prompt_result.output
        return final_prompt