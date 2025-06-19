from typing import Any, Dict
from models import SceneInput, FinalVeoPrompt, Character
from session_manager import SessionManager
from agents import (
    context_analysis_agent,
    final_assembly_agent,
    character_enrichment_agent,
    camera_enrichment_agent,
    sounds_enrichment_agent,
    realism_filter_agent
)
from config import Config

class Orchestrator:
    def __init__(self, session: SessionManager) -> None:
        self.session = session
        # Validate API keys on initialization
        Config.validate_api_keys()

    def process_user_input(self, structured_inputs: Dict[str, str]) -> FinalVeoPrompt:
        """
        Process structured inputs using hybrid approach:
        1. Context analysis (combined)
        2. Selective field enhancement
        3. Final assembly
        """
        # Check if core agents are available
        if not context_analysis_agent or not final_assembly_agent:
            raise RuntimeError("Google API key not set. Cannot process input.")

        # Step 1: Context Analysis (combined processing)
        combined_input = self._combine_inputs(structured_inputs)
        context_result = context_analysis_agent.run_sync(combined_input)
        scene: SceneInput = context_result.output
        self.session.add_scene(scene)

        # Step 2: Update character memory
        self._update_character_memory(scene)

        # Step 3: Selective Field Enhancement
        enriched_fields = self._enrich_critical_fields(structured_inputs)

        # Step 4: Realism validation (skip if agent not available)
        if realism_filter_agent:
            realism_result = realism_filter_agent.run_sync(str(scene))
            is_realistic: bool = realism_result.output
            if not is_realistic:
                raise ValueError("Scene failed realism/style validation.")
        else:
            print("Warning: Skipping realism validation (Anthropic API key not set).")

        # Step 5: Final Assembly with enriched fields
        assembly_input = {
            'scene_context': scene,
            'enriched_fields': enriched_fields,
            'original_inputs': structured_inputs
        }

        prompt_result = final_assembly_agent.run_sync(str(assembly_input))
        final_prompt: FinalVeoPrompt = prompt_result.output
        return final_prompt

    def _combine_inputs(self, inputs: Dict[str, str]) -> str:
        """Combine structured inputs into a single context string."""
        parts = []
        for key, value in inputs.items():
            if value.strip():
                parts.append(f"{key}: {value}")
        return "\n".join(parts)

    def _update_character_memory(self, scene: SceneInput) -> None:
        """Update session memory with character information."""
        for char_name in scene.characters_in_scene:
            if not self.session.get_character(char_name):
                self.session.add_character(Character(
                    name=char_name,
                    character_type="custom",
                    physical_description="",
                    personality_traits=[],
                    consistency_notes=""
                ))

    def _enrich_critical_fields(self, inputs: Dict[str, str]) -> Dict[str, str]:
        """Selectively enrich critical fields that need detailed enhancement."""
        enriched = {}

        # Enrich character description (most important for Veo)
        if inputs.get('character') and character_enrichment_agent:
            try:
                character_prompt = f"""
Enhance this character description for VEO3 video generation:

Guidelines:
- STRICT 8-SECOND LIMIT - All actions must fit within 8 seconds
- Focus on facial expressions and micro-movements VEO3 handles well
- Natural, observable details visible in video
- Subtle authenticity markers (slight asymmetries, natural imperfections)
- No rapid or complex movements
- Keep gestures simple and natural

Input: {inputs['character']}

Return ONLY the VEO3-optimized description. No explanations.
                """.strip()
                result = character_enrichment_agent.run_sync(character_prompt)
                enriched['character'] = result.output
            except Exception as e:
                print(f"Character enrichment failed: {e}")
                enriched['character'] = inputs['character']

        # Enrich camera style (technical details matter)
        if inputs.get('camera_style') and camera_enrichment_agent:
            try:
                camera_prompt = f"""
Create VEO3-optimized camera instructions for this input:

Technical Guidelines (8-second limit):
- Prefer medium shots and medium close-ups
- Keep movements smooth and simple
- Maintain eye-level or slightly above
- Start with stable frame, use subtle zooms
- Allow 1-2 seconds for key moments
- Break down 8 seconds into clear segments

Input: {inputs['camera_style']}

Return ONLY the VEO3-optimized camera instructions with precise timing. No explanations.
                """.strip()
                result = camera_enrichment_agent.run_sync(camera_prompt)
                enriched['camera_style'] = result.output
            except Exception as e:
                print(f"Camera enrichment failed: {e}")
                enriched['camera_style'] = inputs['camera_style']

        # Enrich sounds (audio is critical for video)
        if inputs.get('sounds') and sounds_enrichment_agent:
            try:
                sounds_prompt = f"""
Create VEO3-optimized audio timeline for this input:

Technical Requirements (8-second limit):
- Precise timing markers (e.g., "0:00-0:02:")
- Complete audio timeline for full 8 seconds
- Keep dialogue under 6 seconds total
- Include 0.5s buffer at start/end
- Use natural speech rate (150-170 words/minute)
- Layer primary audio, secondary sounds, and background ambience
- Avoid overlapping complex sounds

Input: {inputs['sounds']}

Return ONLY the 8-second VEO3-optimized sound timeline with precise sync points. No explanations.
                """.strip()
                result = sounds_enrichment_agent.run_sync(sounds_prompt)
                enriched['sounds'] = result.output
            except Exception as e:
                print(f"Sounds enrichment failed: {e}")
                enriched['sounds'] = inputs['sounds']

        # Add scene duration validation
        if any(enriched.values()):
            duration_prompt = f"""
Verify this scene fits within 8 seconds for VEO3:

Character: {enriched.get('character', '')}
Camera: {enriched.get('camera_style', '')}
Sounds: {enriched.get('sounds', '')}

Return 'INVALID' if exceeds 8 seconds or contains incompatible elements, otherwise 'VALID'.
            """.strip()
            try:
                duration_result = character_enrichment_agent.run_sync(duration_prompt)
                if 'INVALID' in duration_result.output:
                    raise ValueError("Scene exceeds 8-second limit or contains incompatible elements for VEO3")
            except Exception as e:
                print(f"Duration validation failed: {e}")

        # Add anti-cartoonish validation
        if any(enriched.values()):
            anti_cartoonish_prompt = f"""
Check if this content contains cartoonish elements:

Character: {enriched.get('character', '')}
Camera: {enriched.get('camera_style', '')}
Sounds: {enriched.get('sounds', '')}

Return 'REJECT' if cartoonish elements found, otherwise 'APPROVE'.
            """.strip()
            try:
                validation_result = character_enrichment_agent.run_sync(anti_cartoonish_prompt)
                if 'REJECT' in validation_result.output:
                    raise ValueError(f"Content contains cartoonish elements: {validation_result.output}")
            except Exception as e:
                print(f"Anti-cartoonish validation failed: {e}")

        return enriched