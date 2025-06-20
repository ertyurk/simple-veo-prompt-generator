from typing import Dict, List
from models import FinalVeoPrompt, MultiScenePrompt
from session_manager import SessionManager
from agents import master_prompt_agent, string_agent
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
        Each prompt will be completely self-contained with consistent character/environment descriptions.
        """
        if not master_prompt_agent:
            raise RuntimeError("Google API key not set. Cannot process input.")

        video_scenes = multi_scene_data.get('video_scenes', [])
        overall_story = multi_scene_data.get('overall_story', '')
        main_characters = multi_scene_data.get('main_characters', '')

        if not video_scenes:
            raise ValueError("No video scenes provided")

        # First pass: Generate consistent elements across all scenes
        consistent_elements = self._build_consistent_elements(video_scenes, overall_story, main_characters)

        # Second pass: Generate individual self-contained prompts
        scene_prompts = []

        for i, scene_data in enumerate(video_scenes):
            scene_num = i + 1

            # Skip empty scenes
            if not any(scene_data.get(field, '').strip() for field in ['character', 'scene_setting', 'action_dialogue']):
                continue

            try:
                # Create fully self-contained prompt for this scene
                scene_prompt = self._create_self_contained_scene_prompt(scene_data, scene_num, consistent_elements)

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

    def _build_consistent_elements(self, video_scenes: List[Dict], overall_story: str, main_characters: str) -> Dict[str, str]:
        """Build consistent character descriptions, props, and environments that will be identical across all scenes."""

        # Collect all unique elements
        all_characters = {}
        all_props = set()
        all_landscapes = set()
        all_sounds = set()

        # Extract and consolidate elements from all scenes
        for scene in video_scenes:
            # Characters - build detailed descriptions
            if scene.get('character', '').strip():
                chars = [char.strip() for char in scene['character'].split(',')]
                for char in chars:
                    if char and char not in all_characters:
                        all_characters[char] = char  # Will be enhanced later

            # Props
            if scene.get('props', '').strip():
                all_props.update([prop.strip() for prop in scene['props'].split(',') if prop.strip()])

            # Landscapes
            if scene.get('landscape', '').strip():
                all_landscapes.update([land.strip() for land in scene['landscape'].split(',') if land.strip()])

            # Sounds
            if scene.get('sounds', '').strip():
                all_sounds.update([sound.strip() for sound in scene['sounds'].split(',') if sound.strip()])

        # Build consistent character descriptions from user inputs
        character_descriptions = self._generate_consistent_character_descriptions(video_scenes, main_characters)

        return {
            'overall_story': overall_story or 'Authentic outdoor adventure vlog',
            'main_characters': main_characters or ', '.join(list(all_characters.keys())[:3]),
            'character_descriptions': character_descriptions,
            'consistent_props': list(all_props)[:5],  # Top 5 most important props
            'consistent_landscape': list(all_landscapes)[:3],  # Key landscape elements
            'consistent_sounds': list(all_sounds)[:7],  # Essential sound elements
            'vlog_style': 'Outdoor Boys authentic handheld vlog style',
            'total_scenes': len(video_scenes)
        }

    def _generate_consistent_character_descriptions(self, video_scenes: List[Dict], main_characters: str) -> Dict[str, str]:
        """Generate consistent character descriptions based on user inputs using AI."""
        if not string_agent:
            return {}

        # Collect all character mentions from scenes
        all_character_info = {}

        for scene in video_scenes:
            if scene.get('character', '').strip():
                # Parse characters from this scene
                chars = [char.strip() for char in scene['character'].split(',')]
                for char in chars:
                    if char:
                        # Store the most detailed description we find
                        if char not in all_character_info or len(scene['character']) > len(all_character_info[char]):
                            all_character_info[char] = scene['character']

        if not all_character_info:
            return {}

        character_descriptions = {}

        for char in list(all_character_info.keys())[:3]:  # Limit to 3 main characters
            # Use the string agent to enhance the user's character description
            enhancement_prompt = f"""
Enhance this character description for professional YouTube vlog consistency: "{all_character_info[char]}"

Character: {char}
User description: {all_character_info[char]}

Make it 15-25 words, focus on visual details, maintain authentic realistic style.
Return ONLY the enhanced description.
"""
            try:
                enhanced_result = string_agent.run_sync(enhancement_prompt)
                character_descriptions[char] = enhanced_result.output.strip()

                # Clean up the description if it has quotes
                if character_descriptions[char].startswith('"') and character_descriptions[char].endswith('"'):
                    character_descriptions[char] = character_descriptions[char][1:-1]

            except Exception as e:
                print(f"Error enhancing character {char}: {e}")
                # Fallback to user's original description
                character_descriptions[char] = all_character_info[char]

        return character_descriptions

    def _create_self_contained_scene_prompt(self, scene_data: Dict, scene_num: int, consistent_elements: Dict) -> str:
        """Create a completely self-contained prompt with consistent descriptions but no references to other scenes."""

        # Start with the scene-specific information
        prompt_parts = [
            f"Create a professional 8-second YouTube vlog scene in the 'Outdoor Boys' style.",
            f"This scene is part of: {consistent_elements['overall_story']}"
        ]

        # Use consistent character descriptions
        if scene_data.get('character', '').strip():
            scene_chars = [char.strip() for char in scene_data['character'].split(',')]
            consistent_char_desc = []
            for char in scene_chars:
                if char in consistent_elements['character_descriptions']:
                    consistent_char_desc.append(consistent_elements['character_descriptions'][char])
                else:
                    consistent_char_desc.append(char)
            prompt_parts.append(f"Characters: {', and '.join(consistent_char_desc)}")

        # Scene-specific details
        if scene_data.get('scene_setting', '').strip():
            prompt_parts.append(f"Scene Setting: {scene_data['scene_setting']}")

        if scene_data.get('action_dialogue', '').strip():
            prompt_parts.append(f"Action & Dialogue: {scene_data['action_dialogue']}")

        if scene_data.get('camera_style', '').strip():
            prompt_parts.append(f"Camera Style: {scene_data['camera_style']}")
        else:
            prompt_parts.append("Camera Style: POV, selfie stick, handheld and natural")

        # Combine scene sounds with consistent background sounds
        scene_sounds = []
        if scene_data.get('sounds', '').strip():
            scene_sounds.extend([s.strip() for s in scene_data['sounds'].split(',') if s.strip()])

        # Add consistent environmental sounds that don't conflict
        for sound in consistent_elements['consistent_sounds']:
            if sound not in scene_sounds:
                scene_sounds.append(sound)

        if scene_sounds:
            prompt_parts.append(f"Sounds: {', '.join(scene_sounds[:7])}")  # Limit to 7 sounds max

        # Landscape with consistent elements
        landscape_elements = []
        if scene_data.get('landscape', '').strip():
            landscape_elements.append(scene_data['landscape'])

        # Add consistent landscape elements that enhance the scene
        for land in consistent_elements['consistent_landscape']:
            if land.lower() not in scene_data.get('landscape', '').lower():
                landscape_elements.append(land)

        if landscape_elements:
            prompt_parts.append(f"Landscape: {', '.join(landscape_elements[:3])}")

        # Props with consistent elements
        props_elements = []
        if scene_data.get('props', '').strip():
            props_elements.extend([p.strip() for p in scene_data['props'].split(',') if p.strip()])

        # Add consistent props that make sense for continuity
        for prop in consistent_elements['consistent_props']:
            if prop not in props_elements:
                props_elements.append(prop)

        if props_elements:
            prompt_parts.append(f"Props: {', '.join(props_elements[:5])}")

        # Final instructions for self-contained, high-quality output
        prompt_parts.extend([
            "\nCRITICAL INSTRUCTIONS:",
            "- Create a completely self-contained prompt with NO references to 'previous scenes' or 'earlier episodes'",
            "- Use the consistent character descriptions provided to maintain continuity",
            "- Generate rich, detailed descriptions matching GREATLY_WORKED_PROMPTS.md quality",
            "- Ensure authentic 'Outdoor Boys' vlog style throughout",
            "- This must work as a standalone 8-second video prompt",
            "- Include specific dialogue and character interactions",
            "- Maintain natural, realistic movements and expressions"
        ])

        return "\n".join(prompt_parts)

    def _format_multi_scene_output(self, scene_prompts: List[Dict], consistent_elements: Dict) -> str:
        """Format all scene prompts into the final multi-video output with completely self-contained prompts."""
        output_parts = [
            f"# Multi-Scene Professional Vlog Prompts\n",
            f"**Total Duration:** {len(scene_prompts) * 8} seconds ({len(scene_prompts)} videos)",
            f"**Overall Story:** {consistent_elements['overall_story']}",
            f"**Main Characters:** {consistent_elements['main_characters']}",
            f"**Style:** {consistent_elements['vlog_style']}\n",
            "**Note:** Each prompt below is completely self-contained and can be used independently for VEO3 generation.\n",
            "---\n"
        ]

        # Add individual video prompts - each completely self-contained
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
        print("Fallback prompt created", character, scene, action)

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