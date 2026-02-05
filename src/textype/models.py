"""Data models for the Textype typing tutor application.

This module defines the UserProfile class and related data structures
for managing user progress and configuration.
"""
import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Tuple
from platformdirs import user_data_dir, user_config_dir
from collections import namedtuple


PROFILES_DIR: str = user_data_dir("textype")
"""Directory where user profile data is stored."""

CONFIG_DIR: str = user_config_dir("textype")
"""Directory where global config data is stored."""

GLOBAL_CONFIG_PATH: str = os.path.join(CONFIG_DIR, "config.json")
"""Path to the global config file."""

# Default configuration values for new profiles
DEFAULT_CONFIG: Dict[str, Any] = {
    "SHOW_QWERTY": True,
    "SHOW_FINGERS": True,
    "HARD_MODE": True,
    "SHOW_STATS_ON_END": True,
    "DRILL_DURATION": 300,
    "SHUFFLE_AFTER": 5,
    "SENTENCE_SOURCE": "local",
    "CODE_SOURCE": "local",
    "SENTENCES_FILE": "sentences.txt",
    "CODE_FILE": "snippets.py",
    "CODE_COMMAND": "",
    "QUOTE_API_URL": "",
    "AI_ENDPOINT": "http://localhost:8000",
    "AI_API_TYPE": "ollama",  # "auto", "ollama", "openai"
    "AI_MODEL": "ollama-7b",
    "AI_API_KEY": "",
    "PRACTICE_MODE": "curriculum",
    "CODE_LANGUAGES": "python,rust,c,cpp",
}

# Initial overrides for new user profiles (different from defaults for better UX)
INITIAL_PROFILE_OVERRIDES: Dict[str, Any] = {
    "SHOW_QWERTY": True,  # Show keyboard by default for new users
    "SHOW_FINGERS": True,  # Show finger guide by default for new users
    "SHOW_STATS_ON_END": True,  # Show stats automatically for new users
    # Other values use DEFAULT_CONFIG values
}


def load_global_config() -> Dict[str, Any]:
    """Load the global configuration from the user's config directory."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(GLOBAL_CONFIG_PATH):
        with open(GLOBAL_CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    try:
        with open(GLOBAL_CONFIG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


GLOBAL_CONFIG: Dict[str, Any] = load_global_config()


@dataclass
class UserProfile:
    """Represents a user profile with progress tracking and configuration.

    Attributes:
        name: Unique identifier for the user profile
        current_lesson_index: Current lesson the user is working on
        wpm_record: Personal best words per minute
        total_drills: Total number of drills completed
        level: User level (currently unused, reserved for future use)
        config_overrides: Profile-specific configuration overrides
    """

    name: str
    current_lesson_index: int = 0
    wpm_record: int = 0
    total_drills: int = 0
    level: int = 1
    # Profile-specific overrides for config
    config_overrides: Dict[str, Any] = field(
        default_factory=lambda: INITIAL_PROFILE_OVERRIDES.copy()
    )

    def get_config(self, key: str) -> Any:
        """Get a configuration value, falling back to defaults.

        Args:
            key: Configuration key to retrieve

        Returns:
            Configuration value (override if exists, otherwise default)
        """
        return self.config_overrides.get(
            key, GLOBAL_CONFIG.get(key, DEFAULT_CONFIG[key])
        )

    @property
    def config(self) -> Dict[str, Any]:
        """Get the merged configuration dictionary (overrides + defaults).

        Returns:
            Complete configuration dictionary with defaults and overrides merged
        """
        merged = DEFAULT_CONFIG.copy()
        merged.update(GLOBAL_CONFIG)
        merged.update(self.config_overrides)
        if not merged.get("AI_API_KEY"):
            try:
                api_type, api_key, model, endpoint = self.get_ai_api_key()
                merged["AI_API_TYPE"] = api_type
                merged["AI_API_KEY"] = api_key
                merged["AI_MODEL"] = model
                merged["AI_ENDPOINT"] = endpoint
            except Exception:
                pass
        return merged

    def get_ai_api_key(self) -> Tuple[Any, ...]:
        """Retrieves the API key for a specified AI service from the environment variables.
        Returns:
            Tuple[str, str, str, str, str]: Tuple containing the API type, api key, model name, and endpoint
        """
        AI_VARS = namedtuple("AI_VARS", ["type", "key", "model", "endpoint"])

        AI_ENV_VARS: Tuple[AI_VARS, ...] = (
            AI_VARS(
                "openai",
                "OPENAI_API_KEY",
                "gpt-5-nano",
                "https://api.openai.com/v1/chat/completions",
            ),
            AI_VARS(
                "deepseek",
                "DEEPSEEK_API_KEY",
                "deepseek-chat",
                "https://api.deepseek.com/v1/chat/completions",
            ),
            AI_VARS(
                "gemini",
                "GEMINI_API_KEY",
                "gemini-2.5-flash-lite",
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent",
            ),
            AI_VARS("ollama", "OLLAMA_API_KEY", "ollama-7b", "http://localhost:8000"),
        )

        for var in AI_ENV_VARS:
            if os.environ.get(var.key):
                return (var.type, os.environ[var.key], var.model, var.endpoint)
        return ()

    def save(self) -> None:
        """Save the user profile to disk.

        Creates the profiles directory if it doesn't exist and writes
        the profile data as JSON.

        Example:
            >>> profile = UserProfile(name="test_user")
            >>> profile.save()  # Saves to ~/.local/share/textype/test_user.json
        """
        if not os.path.exists(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)
        path = os.path.join(PROFILES_DIR, f"{self.name.lower()}.json")
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def load(cls, name: str) -> Optional["UserProfile"]:
        """Load a user profile from disk.

        Args:
            name: Name of the profile to load

        Returns:
            UserProfile instance if found, None otherwise

        Example:
            >>> profile = UserProfile.load("test_user")
            >>> print(profile.name if profile else "Not found")
            test_user
        """
        path = os.path.join(PROFILES_DIR, f"{name.lower()}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return cls(**data)
        return None

    @classmethod
    def list_profiles(cls) -> List[str]:
        """List all available user profiles.

        Returns:
            List of profile names (without .json extension)

        Example:
            >>> profiles = UserProfile.list_profiles()
            >>> print(profiles)
            ['alice', 'bob', 'charlie']
        """
        if not os.path.exists(PROFILES_DIR):
            return []
        return [
            f.replace(".json", "")
            for f in os.listdir(PROFILES_DIR)
            if f.endswith(".json")
        ]

    @classmethod
    def delete(cls, name: str) -> bool:
        """Delete a user profile from disk.

        Args:
            name: Name of the profile to delete

        Returns:
            True if profile was deleted, False if profile didn't exist

        Example:
            >>> UserProfile.delete("old_user")
            True
        """
        path = os.path.join(PROFILES_DIR, f"{name.lower()}.json")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def get_current_lesson_name(self) -> str:
        """Get the display name of the current lesson.

        Returns:
            Lesson name string, or "Unknown" if index out of range.
        """
        try:
            from textype.curriculum import LESSONS

            if self.current_lesson_index < len(LESSONS):
                return LESSONS[self.current_lesson_index]["name"]
        except (ImportError, IndexError):
            pass
        return "Unknown"


FingerDimensions = namedtuple("FingerDimensions", ["height", "width"])
"""Dimensions for finger visualization columns.

Attributes:
    height: Vertical height of the finger column
    width: Horizontal width of the finger column
"""

FINGER_HEIGHTS: Dict[str, FingerDimensions] = {
    "L1": FingerDimensions(4, 7),
    "L2": FingerDimensions(6, 7),
    "L3": FingerDimensions(7, 7),
    "L4": FingerDimensions(6, 7),
    "THUMB": FingerDimensions(2, 20),
    "R1": FingerDimensions(6, 7),
    "R2": FingerDimensions(7, 7),
    "R3": FingerDimensions(6, 7),
    "R4": FingerDimensions(4, 7),
}
"""Dimensions for each finger's visualization column.

Keys correspond to finger identifiers:
- L1-L4: Left hand fingers (pinky to index)
- R1-R4: Right hand fingers (index to pinky)
- THUMB: Space bar thumb
"""

MAX_FINGER_HEIGHT: int = max(
    dimensions.height for dimensions in FINGER_HEIGHTS.values()
)
"""Maximum height among all finger columns for alignment purposes."""
