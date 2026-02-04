"""Unit tests for the models module."""

import json
import os
from unittest.mock import patch

import pytest

from textype.models import UserProfile, DEFAULT_CONFIG, INITIAL_PROFILE_OVERRIDES


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
