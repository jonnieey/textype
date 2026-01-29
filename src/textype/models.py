# models.py
import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, Any

PROFILES_DIR = "profiles"


@dataclass
class UserProfile:
    name: str
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

    def save(self):
        if not os.path.exists(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)
        path = os.path.join(PROFILES_DIR, f"{self.name.lower()}.json")
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def load(cls, name: str):
        path = os.path.join(PROFILES_DIR, f"{name.lower()}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return cls(**data)
        return None

    @classmethod
    def list_profiles(cls):
        if not os.path.exists(PROFILES_DIR):
            return []
        return [
            f.replace(".json", "")
            for f in os.listdir(PROFILES_DIR)
            if f.endswith(".json")
        ]
