"""Textual widgets and screens for the Textype typing tutor UI.

This module defines custom widgets and modal screens used in the
Textype application, including finger visualization, statistics display,
and profile selection.
"""
from typing import Optional, Dict, Any, Tuple
from textual.app import ComposeResult
from textual.widgets import Static, Label, Button, Input, ListItem, ListView, Select
from textual.containers import (
    Container,
    Center,
    Middle,
    Horizontal,
    ScrollableContainer,
)
from textual.screen import Screen
from textual.binding import Binding


from textype.models import UserProfile, MAX_FINGER_HEIGHT, DEFAULT_CONFIG


class FingerColumn(Container):
    """A visual representation of a single finger's column.

    Displays a vertical column representing a finger with adjustable
    height and width for the finger guide visualization.

    Attributes:
        fid: Finger identifier (e.g., "L1", "R2", "THUMB")
        height: Vertical height of the finger column
        width: Horizontal width of the finger column
    """

    def __init__(self, fid: str, height: int, width: int) -> None:
        """Initialize a finger column.

        Args:
            fid: Finger identifier
            height: Column height
            width: Column width
        """
        super().__init__(classes="finger-column")
        self.fid = fid
        self.height = height
        self.width = width

    def compose(self) -> ComposeResult:
        """Compose the finger column widget.

        Creates a spacer for alignment and the finger body with
        appropriate styling.

        Yields:
            Widgets for the finger column
        """
        spacer = Static("")
        spacer.styles.height = MAX_FINGER_HEIGHT - self.height
        yield spacer

        body = Static(
            self.fid if self.fid != "THUMB" else "   ",
            id=self.fid,
            classes="finger-body",
        )
        body.styles.height = self.height
        body.styles.width = self.width
        yield body


class StatsScreen(Screen):
    """A modal screen that displays the results of a typing drill.

    Shows WPM, accuracy, and error count after a drill session completes.
    """

    def __init__(
        self, wpm: int, accuracy: int, errors: int, passed: bool = True
    ) -> None:
        """Initialize the statistics screen.

        Args:
            wpm: Words per minute achieved
            accuracy: Accuracy percentage
            errors: Number of errors made
            passed: Whether the lesson requirements were met
        """
        super().__init__()
        self.wpm = wpm
        self.accuracy = accuracy
        self.errors = errors
        self.passed = passed

    def compose(self) -> ComposeResult:
        """Compose the statistics screen.

        Yields:
            Widgets for the statistics display
        """
        with Center():
            with Middle(id="stats-modal"):
                yield Label("DRILL COMPLETE", id="stats-title")
                yield Label(f"WPM: {self.wpm}", classes="stat-line")
                yield Label(f"Accuracy: {self.accuracy}%", classes="stat-line")
                yield Label(f"Errors: {self.errors}", classes="stat-line")
                with Horizontal():
                    yield Button("Repeat Lesson", variant="default", id="repeat-button")
                    if self.passed:
                        yield Button("Next Drill", variant="primary", id="next-button")

    def on_mount(self) -> None:
        """Focus the appropriate button when screen mounts."""
        if self.passed:
            self.query_one("#next-button").focus()
        else:
            self.query_one("#repeat-button").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press to dismiss screen.

        Args:
            event: Button press event
        """
        if event.button.id == "repeat-button":
            self.dismiss("repeat")
        else:
            self.dismiss("next")


class ConfigWidgetFactory:
    """Factory for creating configuration widgets based on configuration types."""

    @staticmethod
    def create_widget(
        key: str,
        label: str,
        effective_value: Any,
        default_value: Any,
        modified_config: Dict[str, Any],
    ) -> Tuple[Any, str]:
        """Create an appropriate widget for a configuration value.

        Args:
            key: Configuration key
            label: Display label
            effective_value: Current effective value (defaults + overrides)
            default_value: Default value from DEFAULT_CONFIG
            modified_config: Dictionary to track modified configuration

        Returns:
            Tuple of (widget, widget_id)
        """
        expected_type = type(default_value)

        if expected_type == bool:
            return ConfigWidgetFactory._create_boolean_widget(key, effective_value)
        elif key in ("PRACTICE_MODE", "SENTENCE_SOURCE", "CODE_SOURCE"):
            return ConfigWidgetFactory._create_select_widget(key, effective_value)
        else:
            return ConfigWidgetFactory._create_input_widget(
                key, label, effective_value, default_value
            )

    @staticmethod
    def _create_boolean_widget(key: str, effective_value: Any) -> Tuple[Select, str]:
        """Create a Select dropdown for boolean values."""
        if isinstance(effective_value, bool):
            str_value = "True" if effective_value else "False"
        else:
            str_value = str(effective_value).strip()
            if str_value.lower() in ("true", "yes", "1", "on"):
                str_value = "True"
            elif str_value.lower() in ("false", "no", "0", "off"):
                str_value = "False"
            else:
                str_value = "False"

        select_widget = Select(
            options=[("True", "True"), ("False", "False")],
            value=str_value,
            id=f"input-{key}",
            classes="config-select",
        )
        return select_widget, f"input-{key}"

    @staticmethod
    def _create_select_widget(key: str, effective_value: Any) -> Tuple[Select, str]:
        """Create a Select dropdown for mode/source selection."""
        if key == "PRACTICE_MODE":
            options = [
                ("curriculum", "curriculum"),
                ("sentences", "sentences"),
                ("code", "code"),
            ]
            default_val = "curriculum"
        elif key == "SENTENCE_SOURCE":
            options = [
                ("local", "local"),
                ("file", "file"),
                ("api", "api"),
                ("cmd", "cmd"),
                ("ai", "ai"),
            ]
            default_val = "api"
        else:  # CODE_SOURCE
            options = [
                ("local", "local"),
                ("file", "file"),
                ("cmd", "cmd"),
                ("ai", "ai"),
            ]
            default_val = "local"

        str_value = str(effective_value).strip()
        if not str_value or str_value == "":
            str_value = default_val

        select_widget = Select(
            options=options,
            value=str_value,
            id=f"input-{key}",
            classes="config-select",
        )
        return select_widget, f"input-{key}"

    @staticmethod
    def _create_input_widget(
        key: str, label: str, effective_value: Any, default_value: Any
    ) -> Tuple[Input, str]:
        """Create an Input widget for other configuration types."""
        placeholder_text = (
            f"Default: {default_value}"
            if default_value
            else f"Enter {label.lower()}..."
        )
        input_widget = Input(
            value=str(effective_value),
            placeholder=placeholder_text,
            id=f"input-{key}",
            classes="config-input",
        )
        return input_widget, f"input-{key}"


class ProfileInfoScreen(Screen):
    """Screen displaying profile information and editable configuration."""

    def __init__(self, profile: UserProfile) -> None:
        """Initialize the profile info screen.

        Args:
            profile: The user profile to display
        """
        super().__init__()
        self.profile = profile
        self.original_config = profile.config_overrides.copy()
        self.modified_config = profile.config_overrides.copy()

    def compose(self) -> ComposeResult:
        """Compose the profile info screen.

        Yields:
            Widgets for profile information and editable configuration
        """
        with Center():
            with Middle(id="profile-info-modal"):
                yield Label(f"PROFILE: {self.profile.name.upper()}", id="stats-title")

                # Read-only profile information in a scrollable container
                with ScrollableContainer(classes="profile-section"):
                    yield Label("Profile Information", classes="section-title")
                    yield Label(
                        f"Current Lesson: {self.profile.get_current_lesson_name()}",
                        classes="stat-line",
                    )
                    yield Label(
                        f"Current Lesson Index: {self.profile.current_lesson_index}",
                        classes="stat-line",
                    )
                    yield Label(
                        f"WPM Record: {self.profile.wpm_record}", classes="stat-line"
                    )
                    yield Label(
                        f"Total Drills: {self.profile.total_drills}",
                        classes="stat-line",
                    )
                    yield Label(f"Level: {self.profile.level}", classes="stat-line")

                # Editable configuration
                with ScrollableContainer(classes="config-section"):
                    yield Label("Configuration Settings", classes="section-title")

                    # UI Configuration
                    yield Label("UI Configuration", classes="subsection-title")
                    yield self._create_config_widget("SHOW_QWERTY", "Show Keyboard")
                    yield self._create_config_widget(
                        "SHOW_FINGERS", "Show Finger Guide"
                    )
                    yield self._create_config_widget(
                        "SHOW_STATS_ON_END", "Show Stats Automatically"
                    )
                    yield self._create_config_widget(
                        "HARD_MODE", "Hard Mode (errors prevent progress)"
                    )

                    # Practice Settings
                    yield Label("Practice Settings", classes="subsection-title")
                    yield self._create_config_widget(
                        "DRILL_DURATION", "Drill Duration (seconds)"
                    )
                    yield self._create_config_widget(
                        "SHUFFLE_AFTER", "Shuffle After (repetitions)"
                    )
                    yield self._create_config_widget("PRACTICE_MODE", "Practice Mode")
                    yield self._create_config_widget(
                        "CODE_LANGUAGES", "Code Languages (comma-separated)"
                    )

                    # Sentence Generation
                    yield Label("Sentence Generation", classes="subsection-title")
                    yield self._create_config_widget(
                        "SENTENCE_SOURCE", "Sentence Source"
                    )
                    yield self._create_config_widget(
                        "SENTENCES_FILE", "Sentences File Path"
                    )
                    yield self._create_config_widget("QUOTE_API_URL", "Quote API URL")
                    yield self._create_config_widget(
                        "CODE_COMMAND", "Command for Sentence Generation"
                    )
                    yield self._create_config_widget("AI_ENDPOINT", "AI Endpoint URL")

                    # Code Generation
                    yield Label("Code Generation", classes="subsection-title")
                    yield self._create_config_widget("CODE_SOURCE", "Code Source")
                    yield self._create_config_widget(
                        "CODE_FILE", "Code Snippets File Path"
                    )

                # Action buttons
                with Horizontal(classes="action-buttons"):
                    yield Button("Save Changes", variant="primary", id="save-button")
                    yield Button("Cancel", variant="default", id="cancel-button")
                    yield Button("Delete Profile", variant="error", id="delete-button")

    def _create_config_widget(self, key: str, label: str) -> Horizontal:
        """Create an appropriate widget for a configuration value."""
        # Get the current effective value (defaults + overrides)
        effective_value = self.profile.config.get(key, "")
        default_value = DEFAULT_CONFIG.get(key, "")

        # Use factory to create widget
        widget, widget_id = ConfigWidgetFactory.create_widget(
            key, label, effective_value, default_value, self.modified_config
        )

        return Horizontal(
            Label(f"{label}:", classes="config-label"), widget, classes="config-row"
        )

    def on_mount(self) -> None:
        """Focus the first config widget when screen mounts."""
        first_widget = self.query_one(".config-input, .config-select")
        if first_widget:
            first_widget.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes to update modified configuration."""
        self._handle_config_change(event.input.id, event.value)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes to update modified configuration."""
        self._handle_config_change(event.select.id, event.select.value)

    def _handle_config_change(self, widget_id: str, value: str) -> None:
        """Update modified configuration when any config widget changes."""
        if widget_id and widget_id.startswith("input-"):
            key = widget_id.replace("input-", "")
            default_value = DEFAULT_CONFIG.get(key)

            # Determine expected type from DEFAULT_CONFIG
            expected_type = type(default_value)

            # Convert to appropriate type and compare with default
            if expected_type == bool:
                # Handle boolean values
                if value.lower() in ("true", "yes", "1", "on"):
                    converted_value = True
                elif value.lower() in ("false", "no", "0", "off"):
                    converted_value = False
                else:
                    # Invalid boolean, keep as string for now
                    converted_value = value

                # Compare with default (after conversion)
                if (
                    isinstance(converted_value, bool)
                    and converted_value == default_value
                ):
                    # Same as default, remove override if present
                    self.modified_config.pop(key, None)
                else:
                    # Different from default or invalid, store override
                    self.modified_config[key] = converted_value

            elif expected_type == int:
                if value.strip() == "":
                    # Empty string for int field - treat as "use default"
                    self.modified_config.pop(key, None)
                else:
                    try:
                        converted_value = int(value)
                        if converted_value == default_value:
                            # Same as default, remove override
                            self.modified_config.pop(key, None)
                        else:
                            # Different from default, store override
                            self.modified_config[key] = converted_value
                    except ValueError:
                        # Invalid integer, keep as string for now
                        self.modified_config[key] = value
            else:
                # String or other types
                if value == default_value:
                    # Same as default, remove override
                    self.modified_config.pop(key, None)
                else:
                    # Different from default, store override
                    self.modified_config[key] = value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press actions."""
        if event.button.id == "save-button":
            # Save changes to profile
            self.profile.config_overrides = self.modified_config.copy()
            self.profile.save()
            self.dismiss(("saved", self.profile.name))

        elif event.button.id == "cancel-button":
            # Discard changes and return
            self.dismiss(("cancelled", None))

        elif event.button.id == "delete-button":
            self._show_delete_confirmation(
                self.profile.name, self._handle_profile_deletion
            )

    def _handle_profile_deletion(self, confirmed: bool, profile_name: str) -> None:
        """Handle the result of profile deletion confirmation.

        Args:
            confirmed: Whether deletion was confirmed
            profile_name: Name of the profile to delete
        """
        if confirmed:
            self.dismiss(("delete", profile_name))
        # else do nothing (stay on screen)


class ProfileSelectScreen(Screen):
    """Screen to select or create a user profile.

    Allows users to choose an existing profile or create a new one
    before starting typing practice.
    """

    BINDINGS = [
        Binding("delete", "delete_profile", "Delete Selected Profile"),
    ]

    def __init__(self) -> None:
        """Initialize the profile selection screen."""
        super().__init__()
        self.selected_profile: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the profile selection screen.

        Yields:
            Widgets for profile selection and creation
        """
        with Center():
            with Middle(id="profile-modal"):
                yield Label("SELECT OR CREATE PROFILE", id="stats-title")
                yield Input(
                    placeholder="Enter new profile name...", id="new-profile-input"
                )
                yield ListView(id="profile-list")
                yield Label(
                    "Press Enter to Select/Create • Press Delete to delete selected profile",
                    classes="stat-line",
                )
                yield Button(
                    "Delete Selected Profile",
                    variant="error",
                    id="delete-button",
                    disabled=True,
                )

    async def on_mount(self) -> None:
        """Initialize the screen with profile list and focus."""
        await self.refresh_list()
        lst = self.query_one("#profile-list")
        if lst.children:
            lst.focus()
            lst.index = 0
        else:
            self.query_one("#new-profile-input").focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Update selected profile when list item is highlighted.

        Args:
            event: List view highlight event
        """
        if event.item is None:
            self.selected_profile = None
            delete_button = self.query_one("#delete-button")
            delete_button.disabled = True
            return

        self.selected_profile = event.item.id
        delete_button = self.query_one("#delete-button")
        delete_button.disabled = False

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle existing profile selection.

        Args:
            event: List view selection event
        """
        profile = UserProfile.load(event.item.id)
        self.dismiss(profile)

    def action_delete_profile(self) -> None:
        """Handle delete key press to delete selected profile."""
        if self.selected_profile:
            delete_button = self.query_one("#delete-button")
            if not delete_button.disabled:
                # Simulate delete button press
                self.on_button_pressed(Button.Pressed(delete_button))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press for delete button.

        Args:
            event: Button press event
        """
        if event.button.id == "delete-button":
            if self.selected_profile:
                self._show_delete_confirmation(
                    self.selected_profile, self._handle_profile_list_deletion
                )

    def _show_delete_confirmation(self, profile_name: str, callback) -> None:
        """Show confirmation screen for profile deletion.

        Args:
            profile_name: Name of the profile to delete
            callback: Function to call with confirmation result
        """

        def handle_confirmation(result: tuple):
            action, confirmed = result
            if action == "confirm":
                callback(confirmed, profile_name)

        self.app.push_screen(
            ConfirmationScreen(f"Delete profile '{profile_name}'?"),
            handle_confirmation,
        )

    def _handle_profile_list_deletion(self, confirmed: bool, profile_name: str) -> None:
        """Handle deletion of a profile from the profile list.

        Args:
            confirmed: Whether deletion was confirmed
            profile_name: Name of the profile to delete
        """
        if not confirmed:
            return

        # Delete the profile
        deleted = UserProfile.delete(profile_name)
        if deleted:
            self.notify(f"Profile '{profile_name}' deleted.")
            # Clear current profile if it matches the deleted one
            if (
                hasattr(self.app, "profile")
                and self.app.profile
                and self.app.profile.name == profile_name
            ):
                self.app.profile = None
                self.notify("Current profile cleared. Please select a new profile.")
            # Refresh list and reset selection
            self.selected_profile = None
            delete_button = self.query_one("#delete-button")
            delete_button.disabled = True

            async def refresh_and_update_focus():
                await self.refresh_list()
                lst = self.query_one("#profile-list")
                if lst.children:
                    lst.focus()
                    lst.index = 0
                else:
                    self.query_one("#new-profile-input").focus()

            self.app.run_worker(refresh_and_update_focus)
        else:
            self.notify(
                f"Failed to delete profile '{profile_name}'.",
                severity="error",
            )

    async def refresh_list(self) -> None:
        """Refresh the list of available profiles.

        Loads profiles from disk and populates the list view.
        """
        lst = self.query_one("#profile-list")
        await lst.clear()
        for p in UserProfile.list_profiles():
            lst.append(ListItem(Label(p.capitalize()), id=p))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle new profile creation.

        Args:
            event: Input submission event containing profile name
        """
        name = event.value.strip()
        if name:
            profile = UserProfile.load(name) or UserProfile(name=name)
            profile.save()
            self.dismiss(profile)


class ConfirmationScreen(Screen):
    """A simple confirmation dialog screen.

    Returns either ("confirm", True) or ("confirm", False) based on user choice.
    """

    def __init__(self, message: str) -> None:
        """Initialize confirmation screen.

        Args:
            message: The message to display
        """
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the confirmation screen.

        Yields:
            Widgets for confirmation dialog
        """
        with Center():
            with Middle(id="confirmation-modal"):
                yield Label(self.message, id="confirmation-title")
                with Horizontal():
                    yield Button("Yes", variant="error", id="yes-button")
                    yield Button("No", variant="primary", id="no-button")

    def on_mount(self) -> None:
        """Focus the No button when screen mounts."""
        self.query_one("#no-button").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press to dismiss screen.

        Args:
            event: Button press event
        """
        if event.button.id == "yes-button":
            self.dismiss(("confirm", True))
        else:
            self.dismiss(("confirm", False))
