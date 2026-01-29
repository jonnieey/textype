import time
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Horizontal

# Constants for finger mapping
FINGER_MAP = {
    "Q": "L-PINKY", "A": "L-PINKY", "Z": "L-PINKY", "1": "L-PINKY",
    "W": "L-RING", "S": "L-RING", "X": "L-RING", "2": "L-RING",
    "E": "L-MIDDLE", "D": "L-MIDDLE", "C": "L-MIDDLE", "3": "L-MIDDLE",
    "R": "L-INDEX", "F": "L-INDEX", "V": "L-INDEX", "4": "L-INDEX",
    "T": "L-INDEX", "G": "L-INDEX", "B": "L-INDEX", "5": "L-INDEX",
    "Y": "R-INDEX", "H": "R-INDEX", "N": "R-INDEX", "6": "R-INDEX",
    "U": "R-INDEX", "J": "R-INDEX", "M": "R-INDEX", "7": "R-INDEX",
    "I": "R-MIDDLE", "K": "R-MIDDLE", ",": "R-MIDDLE", "8": "R-MIDDLE",
    "O": "R-RING", "L": "R-RING", ".": "R-RING", "9": "R-RING",
    "P": "R-PINKY", ";": "R-PINKY", "/": "R-PINKY", "0": "R-PINKY",
    " ": "THUMBS"
}

ROWS = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["SPACE"]
]

class Key(Static): pass
class FingerIndicator(Static): pass

class TypingTutor(App):
    CSS = """
    #stats-bar {
        height: 3;
        content-align: center middle;
        background: $accent-darken-3;
        color: white;
        text-style: bold;
    }
    #typing-area {
        height: 7;
        content-align: center middle;
        background: $surface;
        margin: 1;
        border: solid $primary;
    }
    .row { height: 3; align: center middle; }
    Key {
        width: 6; height: 3;
        background: $panel;
        border: solid $primary;
        content-align: center middle;
        margin: 0 1;
    }
    #key-space { width: 30; }
    
    .active-key { background: $accent; color: white; text-style: bold; }
    
    #finger-bar { height: 3; align: center middle; margin-top: 1; }
    FingerIndicator {
        padding: 0 2;
        border: solid $primary-darken-2;
        margin: 0 1;
        background: $surface;
    }
    .active-finger { background: $warning; color: black; text-style: bold; border: solid white; }
    """

    def __init__(self):
        super().__init__()
        self.target_text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        self.typed_text = ""
        self.start_time = None
        self.total_errors = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("WPM: 0 | Accuracy: 100% | Errors: 0", id="stats-bar")
        yield Static("", id="typing-area")
        
        with Vertical(id="keyboard"):
            for i, row in enumerate(ROWS):
                with Horizontal(classes="row"):
                    for char in row:
                        yield Key(char, id=f"key-{char.lower()}")

        with Horizontal(id="finger-bar"):
            for f in ["L-PINKY", "L-RING", "L-MIDDLE", "L-INDEX", "THUMBS", "R-INDEX", "R-MIDDLE", "R-RING", "R-PINKY"]:
                yield FingerIndicator(f, id=f)
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_display()

    def on_key(self, event) -> None:
        if not self.start_time:
            self.start_time = time.time()

        if event.key == "backspace":
            self.typed_text = self.typed_text[:-1]
        elif len(event.key) == 1:
            char_in = event.key.upper()
            
            # Error check before appending
            expected_idx = len(self.typed_text)
            if expected_idx < len(self.target_text):
                if char_in != self.target_text[expected_idx]:
                    self.total_errors += 1
            
            self.typed_text += char_in
        
        self.refresh_display()

    def calculate_metrics(self):
        if not self.start_time or not self.typed_text:
            return 0, 100
        
        elapsed_minutes = (time.time() - self.start_time) / 60
        # WPM standard: (chars / 5) / minutes
        wpm = round((len(self.typed_text) / 5) / elapsed_minutes) if elapsed_minutes > 0 else 0
        
        accuracy = round(((len(self.typed_text) - self.total_errors) / max(1, len(self.typed_text))) * 100)
        return wpm, accuracy

    def refresh_display(self) -> None:
        # 1. Update Text & Stats
        wpm, acc = self.calculate_metrics()
        self.query_one("#stats-bar").update(f"WPM: {wpm} | Accuracy: {acc}% | Errors: {self.total_errors}")

        rich_text = ""
        for i, char in enumerate(self.target_text):
            if i < len(self.typed_text):
                color = "green" if self.typed_text[i] == self.target_text[i] else "red"
                rich_text += f"[{color}]{char}[/]"
            elif i == len(self.typed_text):
                rich_text += f"[reverse]{char}[/]"
            else:
                rich_text += char
        self.query_one("#typing-area").update(rich_text)

        # 2. Update Highlighting
        self.query("Key").remove_class("active-key")
        self.query("FingerIndicator").remove_class("active-finger")

        if len(self.typed_text) < len(self.target_text):
            next_char = self.target_text[len(self.typed_text)]
            key_id = f"#key-{'space' if next_char == ' ' else next_char.lower()}"
            try: self.query_one(key_id).add_class("active-key")
            except: pass

            finger = FINGER_MAP.get(next_char, "")
            if finger: self.query_one(f"#{finger}").add_class("active-finger")

if __name__ == "__main__":
    app = TypingTutor()
    app.run()
