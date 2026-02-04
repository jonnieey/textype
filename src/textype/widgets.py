"""Textual widgets and screens for the Textype typing tutor UI.

This module defines custom widgets and modal screens used in the
Textype application, including finger visualization, statistics display,
and profile selection.
"""
from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static, Label, Button, Input, ListItem, ListView
from textual.containers import Container, Center, Middle, Horizontal
from textual.screen import Screen
from textual.binding import Binding

import textype.config as config

from textype.models import UserProfile


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
        spacer.styles.height = config.MAX_FINGER_HEIGHT - self.height
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


class ProfileInfoScreen(Screen):
    """Screen displaying profile information and management options."""

    def __init__(self, profile: UserProfile) -> None:
        """Initialize the profile info screen.

        Args:
            profile: The user profile to display
        """
        super().__init__()
        self.profile = profile

    def compose(self) -> ComposeResult:
        """Compose the profile info screen.

        Yields:
            Widgets for profile information and actions
        """
        with Center():
            with Middle(id="profile-info-modal"):
                yield Label(f"PROFILE: {self.profile.name.upper()}", id="stats-title")
                yield Label(
                    f"Current Lesson: {self.profile.get_current_lesson_name()}",
                    classes="stat-line",
                )
                yield Label(
                    f"WPM Record: {self.profile.wpm_record}", classes="stat-line"
                )
                yield Label(
                    f"Total Drills: {self.profile.total_drills}", classes="stat-line"
                )
                with Horizontal():
                    yield Button("Delete Profile", variant="error", id="delete-button")
                    yield Button("Back", variant="primary", id="back-button")

    def on_mount(self) -> None:
        """Focus the back button when screen mounts."""
        self.query_one("#back-button").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press to dismiss screen.

        Args:
            event: Button press event
        """
        if event.button.id == "delete-button":
            # Show confirmation screen
            def handle_confirmation(result: tuple):
                action, confirmed = result
                if action == "confirm" and confirmed:
                    self.dismiss(("delete", self.profile.name))
                # else do nothing (stay on screen)

            self.app.push_screen(
                ConfirmationScreen(f"Delete profile '{self.profile.name}'?"),
                handle_confirmation,
            )
        else:
            self.dismiss(("back", None))


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
                # Show confirmation screen
                def handle_confirmation(result: tuple):
                    action, confirmed = result
                    if action == "confirm" and confirmed:
                        # Delete the profile
                        deleted = UserProfile.delete(self.selected_profile)
                        if deleted:
                            self.notify(f"Profile '{self.selected_profile}' deleted.")
                            # Clear current profile if it matches the deleted one
                            if (
                                hasattr(self.app, "profile")
                                and self.app.profile
                                and self.app.profile.name == self.selected_profile
                            ):
                                self.app.profile = None
                                self.notify(
                                    "Current profile cleared. Please select a new profile."
                                )
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
                                f"Failed to delete profile '{self.selected_profile}'.",
                                severity="error",
                            )

                self.app.push_screen(
                    ConfirmationScreen(f"Delete profile '{self.selected_profile}'?"),
                    handle_confirmation,
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
