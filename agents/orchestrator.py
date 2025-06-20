from typing import Dict, List
from models import FinalVeoPrompt, MultiScenePrompt
from session_manager import SessionManager
from agents import master_prompt_agent
from config import Config
from jinja2 import Environment, FileSystemLoader

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

    def process_multi_scene_input(self, multi_scene_data: Dict) -> str:
        """
        Process multiple video scenes with consistency across all videos.
        Returns formatted multi-scene prompts as a string.
        """
        if not master_prompt_agent:
            raise RuntimeError("Google API key not set. Cannot process input.")

        video_scenes = multi_scene_data.get('video_scenes', [])
        overall_story = multi_scene_data.get('overall_story', '')
        main_characters = multi_scene_data.get('main_characters', '')

        if not video_scenes:
            raise ValueError("No video scenes provided")

        # Generate individual prompts for each scene
        scene_prompts = []
        consistent_elements = self._extract_consistent_elements(video_scenes, overall_story, main_characters)

        for i, scene_data in enumerate(video_scenes):
            scene_num = i + 1

            # Skip empty scenes
            if not any(scene_data.get(field, '').strip() for field in ['character', 'scene_setting', 'action_dialogue']):
                continue

            try:
                # Create context-aware prompt for this scene
                scene_prompt = self._create_scene_prompt(scene_data, scene_num, consistent_elements, len(video_scenes))

                # Generate the prompt using master agent
                prompt_result = master_prompt_agent.run_sync(scene_prompt)
                final_prompt: FinalVeoPrompt = prompt_result.output

                scene_prompts.append({
                    'scene_number': scene_num,
                    'prompt': final_prompt
                })

            except Exception as e:
                print(f"Error generating scene {scene_num}: {e}")
                # Create fallback for this scene
                fallback_prompt = self._create_fallback_prompt({
                    'character': scene_data.get('character', ''),
                    'scene': scene_data.get('scene_setting', ''),
                    'action': scene_data.get('action_dialogue', '')
                })
                scene_prompts.append({
                    'scene_number': scene_num,
                    'prompt': fallback_prompt
                })

        # Format all prompts into the final output
        return self._format_multi_scene_output(scene_prompts, consistent_elements)

    def _extract_consistent_elements(self, video_scenes: List[Dict], overall_story: str, main_characters: str) -> Dict[str, str]:
        """Extract consistent elements across all scenes for continuity."""
        # Analyze all scenes to find common elements
        all_characters = set()
        all_props = set()
        all_landscapes = set()

        for scene in video_scenes:
            if scene.get('character', '').strip():
                all_characters.update([char.strip() for char in scene['character'].split(',')])
            if scene.get('props', '').strip():
                all_props.update([prop.strip() for prop in scene['props'].split(',')])
            if scene.get('landscape', '').strip():
                all_landscapes.update([land.strip() for land in scene['landscape'].split(',')])

        return {
            'overall_story': overall_story or 'Connected outdoor adventure scenes',
            'main_characters': main_characters or ', '.join(list(all_characters)[:3]),  # Limit to main 3
            'common_props': ', '.join(list(all_props)[:5]),  # Common props across scenes
            'common_landscape': ', '.join(list(all_landscapes)[:3]),  # Common landscape elements
            'total_scenes': len(video_scenes),
            'vlog_style': 'Outdoor Boys authentic handheld vlog style'
        }

    def _create_scene_prompt(self, scene_data: Dict, scene_num: int, consistent_elements: Dict, total_scenes: int) -> str:
        """Create a context-aware prompt for a single scene."""
        prompt_parts = [
            f"Create a professional 8-second YouTube vlog scene (Video {scene_num} of {total_scenes}).",
            f"This is part of a {total_scenes}-video series about: {consistent_elements['overall_story']}"
        ]

        # Add scene-specific details
        if scene_data.get('character', '').strip():
            prompt_parts.append(f"Character: {scene_data['character']}")

        if scene_data.get('scene_setting', '').strip():
            prompt_parts.append(f"Scene Setting: {scene_data['scene_setting']}")

        if scene_data.get('action_dialogue', '').strip():
            prompt_parts.append(f"Action & Dialogue: {scene_data['action_dialogue']}")

        if scene_data.get('camera_style', '').strip():
            prompt_parts.append(f"Camera Style: {scene_data['camera_style']}")

        if scene_data.get('sounds', '').strip():
            prompt_parts.append(f"Sounds: {scene_data['sounds']}")

        if scene_data.get('landscape', '').strip():
            prompt_parts.append(f"Landscape: {scene_data['landscape']}")

        if scene_data.get('props', '').strip():
            prompt_parts.append(f"Props: {scene_data['props']}")

        # Add consistency requirements
        prompt_parts.extend([
            f"\nMAINTAIN CONSISTENCY with other scenes:",
            f"- Main characters: {consistent_elements['main_characters']}",
            f"- Overall story theme: {consistent_elements['overall_story']}",
            f"- Vlog style: {consistent_elements['vlog_style']}",
            f"\nGenerate a rich, detailed prompt that matches the quality and style of professional 'Outdoor Boys' vlog content.",
            f"This scene should work as both a standalone 8-second video AND as part of the larger {total_scenes}-video series."
        ])

        return "\n".join(prompt_parts)

    def _format_multi_scene_output(self, scene_prompts: List[Dict], consistent_elements: Dict) -> str:
        """Format all scene prompts into the final multi-video output."""
        output_parts = [
            f"# Multi-Scene Professional Vlog Prompts\n",
            f"**Total Duration:** {len(scene_prompts) * 8} seconds ({len(scene_prompts)} videos)",
            f"**Overall Story:** {consistent_elements['overall_story']}",
            f"**Main Characters:** {consistent_elements['main_characters']}",
            f"**Style:** {consistent_elements['vlog_style']}\n",
            "---\n"
        ]

        # Add individual video prompts
        for scene_data in scene_prompts:
            scene_num = scene_data['scene_number']
            prompt = scene_data['prompt']

            output_parts.extend([
                f"## VIDEO {scene_num}:\n",
                f"Create a realistic, entertaining YouTube vlog video in the style of the channel \"Outdoor Boys.\"\n",
                f"{prompt.main_character_description}. {prompt.scene_setting_description}. {prompt.atmosphere_and_mood}.\n",
                f"The video should look like a genuine, spontaneous scene from a real vlog, not cinematic or overly polished—just natural, handheld, and authentic.\n",
                f"{prompt.core_action_and_dialogue}\n",
                f"**Camera style:** {prompt.camera_style}\n",
                f"**Sounds:** {', '.join(prompt.sounds)}\n",
                f"**Character Personality:** {prompt.main_character_description.split('.')[0] if '.' in prompt.main_character_description else 'Main character'} - {prompt.atmosphere_and_mood}\n",
                f"**Landscape:** {prompt.landscape_notes}\n",
                f"**Props:** {', '.join(prompt.props)}\n",
                "---\n"
            ])

        return "\n".join(output_parts)

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