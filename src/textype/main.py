# main.py

import time
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding

import config
from widgets import FingerColumn, StatsScreen

class TypingTutor(App):
    CSS_PATH = "styles.tcss"
    
    # Added F2 binding for fingers
    BINDINGS = [
        Binding("f1", "toggle_keyboard", "Toggle Keys"),
        Binding("f2", "toggle_fingers", "Toggle Fingers"),
        Binding("f3", "toggle_stats_pref", "Toggle Stats"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.target_text = random.choice(config.SENTENCES)
        self.typed_text = ""
        self.start_time = None
        self.total_errors = 0
        self.show_stats_pref = config.SHOW_STATS_ON_END

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
                    for fid, dimensions in config.FINGER_HEIGHTS.items():
                        yield FingerColumn(fid, dimensions.height, dimensions.width) # (h, w)

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_display()

    # Toggles for UI elements
    def action_toggle_keyboard(self) -> None:
        self.query_one("#keyboard-section").toggle_class("hidden")

    def action_toggle_fingers(self) -> None:
        self.query_one("#finger-guide-wrapper").toggle_class("hidden")

    def action_toggle_stats_pref(self) -> None:
        """Toggle whether stats show automatically at the end."""
        self.show_stats_pref = not self.show_stats_pref
        status = "ON" if self.show_stats_pref else "OFF"
        self.notify(f"Auto-Stats: {status}")

    def on_key(self, event) -> None:
        if len(self.typed_text) >= len(self.target_text):
            if event.key == "enter":
                self.reset_drill()
            elif event.key == "s": # Manual trigger for stats
                self.show_final_stats()
            return

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
        self.check_completion()
    
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

    def reset_drill(self) -> None:
        """Resets the state for a new typing drill."""
        self.target_text = random.choice(config.SENTENCES)
        self.typed_text = ""
        self.start_time = None
        self.total_errors = 0
        self.refresh_display()

    def check_completion(self) -> None:
        if len(self.typed_text) == len(self.target_text):
            if self.show_stats_pref:
                self.show_final_stats()
            else:
                # Prompt user in the typing area
                self.query_one("#typing-area").update(
                    f"\n[#9ece6a]{self.target_text}[/]\n\n"
                    "[reverse] PRESS ENTER FOR NEXT [/]  [#7aa2f7](OR 'S' FOR STATS)[/]"
                )
    def show_final_stats(self) -> None:
         """Calculates metrics and pushes the StatsScreen."""
         elapsed = (time.time() - self.start_time) / 60
         wpm = round((len(self.typed_text) / 5) / elapsed)
         acc = round(((len(self.typed_text) - self.total_errors) 
                     / max(1, len(self.typed_text) + self.total_errors)) * 100)

         self.push_screen(StatsScreen(wpm, acc, self.total_errors), 
                          lambda next: self.reset_drill() if next else None)

if __name__ == "__main__":
    TypingTutor().run()
