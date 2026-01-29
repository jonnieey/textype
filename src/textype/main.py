# main.py

import time
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding

import config
from widgets import FingerColumn

class TypingTutor(App):
    CSS_PATH = "styles.tcss"
    
    # Added F2 binding for fingers
    BINDINGS = [
        Binding("f1", "toggle_keyboard", "Toggle Keys"),
        Binding("f2", "toggle_fingers", "Toggle Fingers"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.target_text = random.choice(config.SENTENCES)
        self.typed_text = ""
        self.start_time = None
        self.total_errors = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-grid"):
            yield Static("", id="stats-bar")
            yield Static("", id="typing-area")

            # Keyboard UI with initial visibility check
            kb_classes = "" if config.SHOW_QWERTY else "hidden"
            with Vertical(id="keyboard-section", classes=kb_classes):
                rows = [
                    ["Q","W","E","R","T","Y","U","I","O","P"],
                    ["A","S","D","F","G","H","J","K","L",";"],
                    ["Z","X","C","V","B","N","M",",",".","/"]
                ]
                for r in rows:
                    with Horizontal(classes="key-row"):
                        for c in r:
                            yield Static(c, classes="key", id=f"key-{config.ID_MAP.get(c, c.lower())}")

                with Horizontal(classes="key-row"):
                    yield Static("SPACE", id="key-space", classes="key")

            # Finger Guide UI with initial visibility check
            fg_classes = "" if config.SHOW_FINGERS else "hidden"
            with Horizontal(id="finger-guide-wrapper", classes=fg_classes):
                with Horizontal(id="finger-guide"):
                    for fid, h in config.FINGER_HEIGHTS.items():
                        yield FingerColumn(fid, h)

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_display()

    # Toggles for UI elements
    def action_toggle_keyboard(self) -> None:
        self.query_one("#keyboard-section").toggle_class("hidden")

    def action_toggle_fingers(self) -> None:
        self.query_one("#finger-guide-wrapper").toggle_class("hidden")

    def on_key(self, event) -> None:
        char = " " if event.key == "space" else event.key

        if not self.start_time and len(char) == 1:
            self.start_time = time.time()

        if event.key == "backspace":
            self.typed_text = self.typed_text[:-1]
        elif len(char) == 1:
            char = char.upper()
            idx = len(self.typed_text)
            if idx < len(self.target_text):
                if char == self.target_text[idx]:
                    self.typed_text += char
                else:
                    self.total_errors += 1
                    if not config.HARD_MODE:
                        self.typed_text += char

        self.refresh_display()

    def refresh_display(self) -> None:
        elapsed = (time.time() - self.start_time) / 60 if self.start_time else 0
        wpm = round((len(self.typed_text) / 5) / elapsed) if elapsed > 0 else 0
        acc = round(((len(self.typed_text) - self.total_errors)
                    / max(1, len(self.typed_text) + self.total_errors)) * 100)

        self.query_one("#stats-bar").update(
            f"WPM: {wpm} | ACCURACY: {acc}% | ERRORS: {self.total_errors}"
        )

        rich = ""
        for i, c in enumerate(self.target_text):
            if i < len(self.typed_text):
                rich += f"[#9ece6a]{c}[/]" if self.typed_text[i] == c else f"[#f7768e]{c}[/]"
            elif i == len(self.typed_text):
                rich += f"[reverse]{c}[/]"
            else:
                rich += c
        self.query_one("#typing-area").update(f"\n\n{rich}")

        self.query(".key").remove_class("active-key")
        self.query(".finger-body").remove_class("active-finger")

        if len(self.typed_text) < len(self.target_text):
            nxt = self.target_text[len(self.typed_text)]
            kid = f"#key-{'space' if nxt == ' ' else config.ID_MAP.get(nxt, nxt.lower())}"
            
            try:
                self.query_one(kid).add_class("active-key")
            except:
                pass

            fid = config.FINGER_MAP.get(nxt)
            if fid:
                try:
                    self.query_one(f"#{fid}").add_class("active-finger")
                except:
                    pass

if __name__ == "__main__":
    TypingTutor().run()
