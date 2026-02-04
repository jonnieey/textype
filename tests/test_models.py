"""Unit tests for the models module."""

import json
import os
from unittest.mock import patch

import pytest

from textype.models import UserProfile, DEFAULT_CONFIG, INITIAL_PROFILE_OVERRIDES


@pytest.fixture
def temp_config_dir(tmp_path):
    """Creates a temporary directory for global config testing."""
    return tmp_path / "config"


@pytest.fixture
def mock_global_config_path(temp_config_dir):
    """Mocks the GLOBAL_CONFIG_PATH constant for tests."""
    config_file = temp_config_dir / "config.json"
    with patch("textype.models.GLOBAL_CONFIG_PATH", str(config_file)):
        yield str(config_file)


class TestConfigHierarchy:
    """Tests the configuration priority: Profile > Global > Default."""

    def test_load_global_config_exists(self, mock_global_config_path):
        """Tests that load_global_config correctly reads a JSON file from disk."""
        from textype.models import load_global_config

        test_data = {"DRILL_DURATION": 999, "AI_MODEL": "test-model"}
        os.makedirs(os.path.dirname(mock_global_config_path), exist_ok=True)
        with open(mock_global_config_path, "w") as f:
            json.dump(test_data, f)

        loaded = load_global_config()
        assert loaded["DRILL_DURATION"] == 999
        assert loaded["AI_MODEL"] == "test-model"

    def test_load_global_config_missing(self, mock_global_config_path):
        """Tests that load_global_config returns an empty dict if file is missing."""
        from textype.models import load_global_config

        if os.path.exists(mock_global_config_path):
            os.remove(mock_global_config_path)

        assert load_global_config() == {}

    def test_hierarchy_global_overrides_default(self):
        """Tests that global configuration takes precedence over built-in defaults."""
        profile = UserProfile(name="test_user")
        # Clear initial overrides to test global vs default
        profile.config_overrides = {}

        mock_global = {"DRILL_DURATION": 123}

        with patch("textype.models.GLOBAL_CONFIG", mock_global):
            # Should pull from Global (123) instead of Default (300)
            assert profile.get_config("DRILL_DURATION") == 123
            # Should still pull other values from Default
            assert profile.get_config("HARD_MODE") == DEFAULT_CONFIG["HARD_MODE"]

    def test_hierarchy_profile_overrides_global(self):
        """Tests that profile-specific settings take precedence over global settings."""
        profile = UserProfile(name="test_user")
        profile.config_overrides = {"DRILL_DURATION": 10}

        mock_global = {"DRILL_DURATION": 999}

        with patch("textype.models.GLOBAL_CONFIG", mock_global):
            # Profile (10) wins over Global (999) and Default (300)
            assert profile.get_config("DRILL_DURATION") == 10

    def test_merged_config_property_logic(self):
        """Tests that the .config property merges all three layers correctly."""
        profile = UserProfile(name="test_user")
        profile.config_overrides = {"SHOW_QWERTY": True}

        mock_global = {
            "DRILL_DURATION": 500,
            "SHOW_QWERTY": False,  # Should be overridden by profile
        }

        with patch("textype.models.GLOBAL_CONFIG", mock_global):
            merged = profile.config

            assert merged["SHOW_QWERTY"] is True  # Profile wins
            assert merged["DRILL_DURATION"] == 500  # Global wins
            assert merged["HARD_MODE"] is True  # Default wins
            # Ensure no keys from DEFAULT_CONFIG are lost
            assert all(key in merged for key in DEFAULT_CONFIG)


@pytest.fixture
def temp_profile_dir(tmp_path):
    """Creates a temporary directory for profile testing."""
    return tmp_path / "profiles"


@pytest.fixture
def mock_profiles_dir(temp_profile_dir):
    """Mocks the PROFILES_DIR constant for tests."""
    with patch("textype.models.PROFILES_DIR", str(temp_profile_dir)):
        yield str(temp_profile_dir)


class TestUserProfile:
    """Tests the UserProfile class for managing user data and settings."""

    def test_profile_creation_defaults(self):
        """Tests that a new profile is created with default values."""
        profile = UserProfile(name="test_user")
        assert profile.name == "test_user"
        assert profile.current_lesson_index == 0
        assert profile.wpm_record == 0
        assert profile.total_drills == 0
        assert profile.level == 1
        assert profile.config_overrides == INITIAL_PROFILE_OVERRIDES

    def test_get_config_with_override(self):
        """Tests retrieving a config value that is overridden in the profile."""
        profile = UserProfile(name="test_user")
        profile.config_overrides["SHOW_QWERTY"] = True
        assert profile.get_config("SHOW_QWERTY") is True

    def test_get_config_with_default(self):
        """Tests retrieving a config value that falls back to the default."""
        profile = UserProfile(name="test_user")
        assert profile.get_config("DRILL_DURATION") == DEFAULT_CONFIG["DRILL_DURATION"]

    def test_config_property(self):
        """Tests that the config property merges overrides and defaults correctly."""
        profile = UserProfile(name="test_user")
        profile.config_overrides["HARD_MODE"] = False
        merged_config = profile.config
        assert merged_config["HARD_MODE"] is False
        assert merged_config["DRILL_DURATION"] == DEFAULT_CONFIG["DRILL_DURATION"]
        assert "SHOW_QWERTY" in merged_config

    def test_save_profile(self, mock_profiles_dir):
        """Tests saving a user profile to a file."""
        profile = UserProfile(name="test_user")
        profile.save()

        expected_path = os.path.join(mock_profiles_dir, "test_user.json")
        assert os.path.exists(expected_path)

        with open(expected_path, "r") as f:
            data = json.load(f)

        assert data["name"] == "test_user"
        assert data["current_lesson_index"] == 0

    def test_load_profile(self, mock_profiles_dir):
        """Tests loading a user profile from a file."""
        profile_data = {
            "name": "test_user",
            "current_lesson_index": 5,
            "wpm_record": 100,
            "total_drills": 50,
            "level": 3,
            "config_overrides": {"SHOW_FINGERS": True},
        }

        profile_path = os.path.join(mock_profiles_dir, "test_user.json")
        os.makedirs(mock_profiles_dir, exist_ok=True)
        with open(profile_path, "w") as f:
            json.dump(profile_data, f)

        profile = UserProfile.load("test_user")

        assert profile is not None
        assert profile.name == "test_user"
        assert profile.current_lesson_index == 5
        assert profile.wpm_record == 100
        assert profile.get_config("SHOW_FINGERS") is True

    def test_load_nonexistent_profile(self, mock_profiles_dir):
        """Tests that loading a non-existent profile returns None."""
        profile = UserProfile.load("nonexistent_user")
        assert profile is None

    def test_list_profiles(self, mock_profiles_dir):
        """Tests listing all available user profiles."""
        os.makedirs(mock_profiles_dir, exist_ok=True)

        # Create some dummy profile files
        (UserProfile(name="alice").save())
        (UserProfile(name="bob").save())

        profiles = UserProfile.list_profiles()

        assert "alice" in profiles
        assert "bob" in profiles
        assert len(profiles) == 2

    def test_delete_profile(self, mock_profiles_dir):
        """Tests deleting a user profile."""
        profile = UserProfile(name="test_user")
        profile.save()

        assert UserProfile.delete("test_user") is True
        assert not os.path.exists(os.path.join(mock_profiles_dir, "test_user.json"))

    def test_delete_nonexistent_profile(self, mock_profiles_dir):
        """Tests that deleting a non-existent profile returns False."""
        assert UserProfile.delete("nonexistent_user") is False

    @patch("textype.curriculum.LESSONS", [{"name": "Lesson 1"}, {"name": "Lesson 2"}])
    def test_get_current_lesson_name(self):
        """Tests retrieving the name of the current lesson."""
        profile = UserProfile(name="test_user", current_lesson_index=1)
        assert profile.get_current_lesson_name() == "Lesson 2"

    @patch("textype.curriculum.LESSONS", [{"name": "Lesson 1"}])
    def test_get_current_lesson_name_out_of_bounds(self):
        """Tests that 'Unknown' is returned for an out-of-bounds lesson index."""
        profile = UserProfile(name="test_user", current_lesson_index=5)
        assert profile.get_current_lesson_name() == "Unknown"
