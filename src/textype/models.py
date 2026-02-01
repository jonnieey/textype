"""Data models for the Textype typing tutor application.

This module defines the UserProfile class and related data structures
for managing user progress and configuration.
"""
import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
from platformdirs import user_data_dir


PROFILES_DIR: str = user_data_dir("textype")
"""Directory where user profile data is stored."""


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
        default_factory=lambda: {
            "SHOW_QWERTY": True,
            "SHOW_FINGERS": True,
            "SHOW_STATS_ON_END": True,
            "HARD_MODE": True,
        }
    )

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
