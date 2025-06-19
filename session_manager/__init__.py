from typing import Dict, List
from models import Character, SceneInput

class SessionManager:
    """
    Manages session state, including character profiles and scene history, to ensure consistency across multi-turn interactions.
    """
    def __init__(self) -> None:
        self.characters: Dict[str, Character] = {}
        self.scenes: List[SceneInput] = []

    def add_character(self, character: Character) -> None:
        self.characters[character.name] = character

    def get_character(self, name: str) -> Character | None:
        return self.characters.get(name)

    def add_scene(self, scene: SceneInput) -> None:
        self.scenes.append(scene)

    def get_last_scene(self) -> SceneInput | None:
        if self.scenes:
            return self.scenes[-1]
        return None

    def get_all_characters(self) -> List[Character]:
        return list(self.characters.values())

    def get_all_scenes(self) -> List[SceneInput]:
        return self.scenes