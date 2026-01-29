from textual.app import ComposeResult
from textual.widgets import Static, Label, Button
from textual.containers import Container, Center, Middle
from textual.screen import Screen
from config import MAX_FINGER_HEIGHT

class FingerColumn(Container):
    """A visual representation of a single finger's column."""
    def __init__(self, fid: str, height: int, width: int):
        super().__init__(classes="finger-column")
        self.fid = fid
        self.height = height

    def compose(self) -> ComposeResult:
        spacer = Static("")
        spacer.styles.height = MAX_FINGER_HEIGHT - self.height
        yield spacer

        body = Static(
            self.fid if self.fid != "THUMB" else "   ",
            id=self.fid,
            classes="finger-body",
        )
        body.styles.height = self.height
        yield body

class StatsScreen(Screen):
    """A modal screen that displays the results of a typing drill."""
    
    def __init__(self, wpm: int, accuracy: int, errors: int):
        super().__init__()
        self.wpm = wpm
        self.accuracy = accuracy
        self.errors = errors

    def compose(self) -> ComposeResult:
        with Center():
            with Middle(id="stats-modal"):
                yield Label("DRILL COMPLETE", id="stats-title")
                yield Label(f"WPM: {self.wpm}", classes="stat-line")
                yield Label(f"Accuracy: {self.accuracy}%", classes="stat-line")
                yield Label(f"Errors: {self.errors}", classes="stat-line")
                yield Button("Next Drill (Enter)", variant="primary", id="next-button")

    def on_mount(self) -> None:
        self.query_one("#next-button").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(True)

    def on_key(self, event) -> None:
        if event.key == "enter":
            self.dismiss(True)
