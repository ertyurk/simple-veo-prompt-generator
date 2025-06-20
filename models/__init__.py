from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class CharacterType(str, Enum):
    BIGFOOT = "bigfoot"
    YETI = "yeti"
    BALLOONFISH = "balloonfish"
    CUSTOM = "custom"  # Allows for generic character creation

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

class CharacterAppearance(BaseModel):
    character_name: str
    appearance_description: str

class VideoScene(BaseModel):
    scene_number: int
    character: str
    scene_setting: str
    action_dialogue: str
    camera_style: str
    sounds: str
    landscape: str
    props: str

class FinalVeoPrompt(BaseModel):
    main_character_description: str
    scene_setting_description: str
    atmosphere_and_mood: str
    core_action_and_dialogue: str
    camera_style: str
    sounds: List[str]
    character_appearances: List[CharacterAppearance] = Field(default_factory=list)
    landscape_notes: str
    props: List[str]

class MultiScenePrompt(BaseModel):
    """Container for multiple video scenes with consistency tracking"""
    overall_story: str
    main_characters: List[str]
    consistent_elements: Dict[str, str]  # Props, locations, etc. that should remain consistent
    video_scenes: List[FinalVeoPrompt]
    total_duration: int  # Total duration in seconds