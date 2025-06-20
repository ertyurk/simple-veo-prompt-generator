from typing import Dict
from models import FinalVeoPrompt
from session_manager import SessionManager
from agents import master_prompt_agent
from config import Config

class Orchestrator:
    def __init__(self, session: SessionManager) -> None:
        self.session = session
        # Validate API keys on initialization
        Config.validate_api_keys()

    def process_user_input(self, structured_inputs: Dict[str, str]) -> FinalVeoPrompt:
        """
        Process user inputs using a single master agent that generates high-quality prompts
        matching the style of GREATLY_WORKED_PROMPTS.md samples.
        """
        # Check if master agent is available
        if not master_prompt_agent:
            raise RuntimeError("Google API key not set. Cannot process input.")

        # Combine all user inputs into a coherent prompt request
        user_prompt = self._create_user_prompt(structured_inputs)

        # Generate the final prompt using the master agent
        try:
            prompt_result = master_prompt_agent.run_sync(user_prompt)
            final_prompt: FinalVeoPrompt = prompt_result.output
            return final_prompt
        except Exception as e:
            print(f"Error generating prompt: {e}")
            # Fallback to basic prompt if master agent fails
            return self._create_fallback_prompt(structured_inputs)

    def _create_user_prompt(self, inputs: Dict[str, str]) -> str:
        """Create a user prompt from the structured inputs."""
        prompt_parts = []

        # Add non-empty inputs to the prompt
        field_labels = {
            'character': 'Character',
            'scene': 'Scene Setting',
            'action': 'Action & Dialogue',
            'camera_style': 'Camera Style',
            'sounds': 'Sounds',
            'landscape': 'Landscape',
            'props': 'Props'
        }

        for key, label in field_labels.items():
            if inputs.get(key, '').strip():
                prompt_parts.append(f"{label}: {inputs[key].strip()}")

        if not prompt_parts:
            return "Create a simple, realistic YouTube vlog scene with natural characters and authentic feel."

        user_prompt = "Create a high-quality YouTube vlog prompt based on these inputs:\n\n" + "\n".join(prompt_parts)
        user_prompt += "\n\nGenerate a rich, detailed prompt that matches the quality and style of professional vlog content, similar to 'Outdoor Boys' channel."

        return user_prompt

    def _create_fallback_prompt(self, inputs: Dict[str, str]) -> FinalVeoPrompt:
        """Create a basic fallback prompt if the master agent fails."""
        character = inputs.get('character', 'A friendly outdoor enthusiast')
        scene = inputs.get('scene', 'in a natural outdoor setting')
        action = inputs.get('action', 'exploring and sharing their adventure')
        print(f"Fallback prompt: {character}, {scene}, {action}")

        return FinalVeoPrompt(
            main_character_description=character,
            scene_setting_description=scene,
            atmosphere_and_mood="Friendly, adventurous, and authentic",
            core_action_and_dialogue=action,
            camera_style="POV, selfie stick, handheld and natural",
            sounds=["Natural outdoor sounds", "Friendly conversation", "Ambient environment"],
            landscape_notes="Natural outdoor environment with authentic details",
            props=["Camera equipment", "Outdoor gear"]
        )