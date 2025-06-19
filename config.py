import os
from typing import Optional

class Config:
    """Configuration management for API keys and environment variables."""

    @staticmethod
    def get_google_api_key() -> Optional[str]:
        """Get Google API key from environment variable."""
        return os.getenv("GOOGLE_API_KEY")

    @staticmethod
    def get_anthropic_api_key() -> Optional[str]:
        """Get Anthropic API key from environment variable."""
        return os.getenv("ANTHROPIC_API_KEY")

    @staticmethod
    def get_openai_api_key() -> Optional[str]:
        """Get OpenAI API key from environment variable."""
        return os.getenv("OPENAI_API_KEY")

    @staticmethod
    def validate_api_keys() -> bool:
        """Validate that required API keys are set."""
        google_key = Config.get_google_api_key()
        anthropic_key = Config.get_anthropic_api_key()

        if not google_key:
            print("Warning: GOOGLE_API_KEY not set. Gemini models will not work.")
        if not anthropic_key:
            print("Warning: ANTHROPIC_API_KEY not set. Claude models will not work.")

        return bool(google_key and anthropic_key)