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
You are a video production expert specializing in VEO3 character generation. Your task is to enhance character descriptions ensuring optimal results with VEO3's capabilities while maintaining absolute realism.

Guidelines for VEO3-optimized character enhancement:
1. STRICT 8-SECOND LIMIT - All actions must fit within 8 seconds
2. VEO3 REALISM CONSTRAINTS:
   - Focus on upper body and facial expressions VEO3 excels at
   - Avoid complex body movements VEO3 struggles with
   - Describe expressions and micro-movements VEO3 handles well
3. PHYSICAL REALISM:
   - Natural, observable details visible in video
   - Realistic movements that VEO3 can render well
   - Subtle authenticity markers (slight asymmetries, natural imperfections)
4. VEO3 LIMITATIONS:
   - No rapid or complex movements
   - No extreme camera angles
   - Keep gestures simple and natural

Input character description:
{inputs['character']}

Return ONLY the VEO3-optimized description focusing on visual realism within 8 seconds. No explanations.
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
You are a VEO3 video expert. Create camera instructions optimized for VEO3's strengths while maintaining a natural vlog style.

VEO3 Camera Guidelines (8-second limit):
1. OPTIMAL ANGLES:
   - Prefer medium shots and medium close-ups
   - Keep camera movements smooth and simple
   - Maintain eye-level or slightly above
2. VEO3 BEST PRACTICES:
   - Start with a stable frame
   - Use subtle zooms VEO3 handles well
   - Allow 1-2 seconds for key moments
3. TIMING:
   - Break down 8 seconds into clear segments
   - Account for natural movement speed
   - Include brief pauses for impact

Input camera style:
{inputs['camera_style']}

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
You are a VEO3 sound design specialist. Create precisely timed audio descriptions for an 8-second video that align with VEO3's capabilities.

VEO3 Audio Requirements:
1. 8-SECOND STRUCTURE:
   - Precise timing markers (e.g., "0:00-0:02:")
   - Complete audio timeline for full 8 seconds
   - Natural pacing that VEO3 can render
2. DIALOGUE & LIPSYNC:
   - Keep dialogue under 6 seconds total
   - Include 0.5s buffer at start/end
   - Mark exact lipsync timing points
   - Use natural speech rate (150-170 words/minute)
3. LAYERED AUDIO:
   - Primary audio (dialogue/main sounds)
   - Secondary sounds (reactions/effects)
   - Background ambience
4. VEO3 OPTIMIZATION:
   - Clear audio perspective changes
   - Simple, clean transitions
   - Avoid overlapping complex sounds

Input sounds description:
{inputs['sounds']}

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
You are a VEO3 timing validator. Verify that all described actions, camera movements, and sounds fit within 8 seconds.

Scene elements to validate:
Character actions: {enriched.get('character', '')}
Camera movements: {enriched.get('camera_style', '')}
Sounds and dialogue: {enriched.get('sounds', '')}

If the scene exceeds 8 seconds or contains elements VEO3 cannot render well, return 'INVALID' with specific issues.
Otherwise, return 'VALID'.
            """.strip()
            try:
                duration_result = character_enrichment_agent.run_sync(duration_prompt)
                if 'INVALID' in duration_result.output:
                    raise ValueError("Scene exceeds 8-second limit or contains incompatible elements for VEO3")
            except Exception as e:
                print(f"Duration validation failed: {e}")

        return enriched