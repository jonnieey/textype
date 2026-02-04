"""Unit tests for the widgets module."""

import pytest
from textual.widgets import Select, Input
from textual.app import App
from textype.widgets import (
    FingerColumn,
    StatsScreen,
    ConfigWidgetFactory,
    ProfileInfoScreen,
    ProfileSelectScreen,
    ConfirmationScreen,
)
from textype.models import UserProfile


@pytest.fixture
def user_profile():
    """Provides a sample UserProfile for testing."""
    return UserProfile(name="test_user")


class TestApp(App):
    pass


class TestFingerColumn:
    """Tests the FingerColumn widget."""

    def test_finger_column_init(self):
        """Tests that the FingerColumn initializes correctly."""
        fc = FingerColumn(fid="L1", height=5, width=7)
        assert fc.fid == "L1"
        assert fc.height == 5
        assert fc.width == 7


class TestStatsScreen:
    """Tests the StatsScreen."""

    @pytest.mark.asyncio
    async def test_stats_screen_init_and_compose(self):
        """Tests initialization and composition of the StatsScreen."""
        screen = StatsScreen(wpm=50, accuracy=95, errors=2, passed=True)
        assert screen.wpm == 50
        assert screen.accuracy == 95
        assert screen.errors == 2
        assert screen.passed is True


class TestConfigWidgetFactory:
    """Tests the ConfigWidgetFactory."""

    # TODO Fix this
    # @pytest.mark.asyncio
    # async def test_create_boolean_widget(self):
    #     """Tests creation of a boolean widget."""
    #     app = TestApp()
    #     async with app.run_test():
    #         widget, _ = ConfigWidgetFactory.create_widget(
    #             "SHOW_QWERTY", "Show Keyboard", False, False, {}
    #         )
    #         assert isinstance(widget, Select)
    #         assert widget.value == "False"

    @pytest.mark.asyncio
    async def test_create_select_widget(self):
        """Tests creation of a select widget."""
        app = TestApp()
        async with app.run_test():
            widget, _ = ConfigWidgetFactory.create_widget(
                "PRACTICE_MODE", "Practice Mode", "curriculum", "curriculum", {}
            )
            assert isinstance(widget, Select)

    @pytest.mark.asyncio
    async def test_create_input_widget(self):
        """Tests creation of an input widget."""
        app = TestApp()
        async with app.run_test():
            widget, _ = ConfigWidgetFactory.create_widget(
                "DRILL_DURATION", "Drill Duration", 300, 300, {}
            )
            assert isinstance(widget, Input)
            assert not widget.password

    @pytest.mark.asyncio
    async def test_create_password_input_widget(self):
        """Tests creation of a password input widget for API keys."""
        app = TestApp()
        async with app.run_test():
            widget, _ = ConfigWidgetFactory.create_widget(
                "AI_API_KEY", "AI API Key", "", "", {}
            )
            assert isinstance(widget, Input)
            assert widget.password is True


class TestProfileInfoScreen:
    """Tests the ProfileInfoScreen."""

    def test_profile_info_screen_init(self, user_profile):
        """Tests initialization of the ProfileInfoScreen."""
        screen = ProfileInfoScreen(profile=user_profile)
        assert screen.profile.name == "test_user"

    def test_handle_config_change_bool(self, user_profile):
        """Tests handling of a boolean configuration change."""
        screen = ProfileInfoScreen(profile=user_profile)
        screen._handle_config_change("input-SHOW_QWERTY", "False")
        assert screen.modified_config["SHOW_QWERTY"] is False

    def test_handle_config_change_int(self, user_profile):
        """Tests handling of an integer configuration change."""
        screen = ProfileInfoScreen(profile=user_profile)
        screen._handle_config_change("input-DRILL_DURATION", "120")
        assert screen.modified_config["DRILL_DURATION"] == 120

    def test_handle_config_change_str(self, user_profile):
        """Tests handling of a string configuration change."""
        screen = ProfileInfoScreen(profile=user_profile)
        screen._handle_config_change("input-SENTENCES_FILE", "new.txt")
        assert screen.modified_config["SENTENCES_FILE"] == "new.txt"


class TestProfileSelectScreen:
    """Tests the ProfileSelectScreen."""

    @pytest.mark.asyncio
    async def test_profile_select_screen_init_and_compose(self):
        """Tests initialization and composition of the ProfileSelectScreen."""
        screen = ProfileSelectScreen()
        assert screen.selected_profile is None


class TestConfirmationScreen:
    """Tests the ConfirmationScreen."""

    @pytest.mark.asyncio
    async def test_confirmation_screen_init_and_compose(self):
        """Tests initialization and composition of the ConfirmationScreen."""
        screen = ConfirmationScreen(message="Are you sure?")
        assert screen.message == "Are you sure?"
