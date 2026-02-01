"""Textual widgets and screens for the Textype typing tutor UI.

This module defines custom widgets and modal screens used in the
Textype application, including finger visualization, statistics display,
and profile selection.
"""
from textual.app import ComposeResult
from textual.widgets import Static, Label, Button, Input, ListItem, ListView
from textual.containers import Container, Center, Middle
from textual.screen import Screen
from textual import events
from config import MAX_FINGER_HEIGHT
from models import UserProfile


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

    def __init__(self, wpm: int, accuracy: int, errors: int) -> None:
        """Initialize the statistics screen.

        Args:
            wpm: Words per minute achieved
            accuracy: Accuracy percentage
            errors: Number of errors made
        """
        super().__init__()
        self.wpm = wpm
        self.accuracy = accuracy
        self.errors = errors

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
                yield Button("Next Drill (Enter)", variant="primary", id="next-button")

    def on_mount(self) -> None:
        """Focus the next button when screen mounts."""
        self.query_one("#next-button").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press to dismiss screen.

        Args:
            event: Button press event
        """
        self.dismiss(True)

    def on_key(self, event: events.Key) -> None:
        """Handle key press to dismiss screen.

        Args:
            event: Key event
        """
        if event.key == "enter":
            self.dismiss(True)


class ProfileSelectScreen(Screen):
    """Screen to select or create a user profile.

    Allows users to choose an existing profile or create a new one
    before starting typing practice.
    """

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
                yield Label("Press Enter to Select/Create", classes="stat-line")

    def on_mount(self) -> None:
        """Initialize the screen with profile list and focus."""
        self.refresh_list()
        lst = self.query_one("#profile-list")
        if lst.children:
            lst.focus()
            lst.index = 0
        else:
            self.query_one("#new-profile-input").focus()

    def refresh_list(self) -> None:
        """Refresh the list of available profiles.

        Loads profiles from disk and populates the list view.
        """
        lst = self.query_one("#profile-list")
        lst.clear()
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

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle existing profile selection.

        Args:
            event: List view selection event
        """
        profile = UserProfile.load(event.item.id)
        self.dismiss(profile)
