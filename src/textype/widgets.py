from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from config import MAX_FINGER_HEIGHT

class FingerColumn(Container):
    """A visual representation of a single finger's column."""
    def __init__(self, fid: str, height: int):
        super().__init__(classes="finger-column")
        self.fid = fid
        self.height = height

    def compose(self) -> ComposeResult:
        spacer = Static("")
        spacer.styles.height = MAX_FINGER_HEIGHT - self.height
        yield spacer

        body = Static(
            self.fid if self.fid != "THUMB" else "---",
            id=self.fid,
            classes="finger-body",
        )
        body.styles.height = self.height
        yield body
