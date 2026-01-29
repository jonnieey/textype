# main.py

import time
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding

import config
from widgets import FingerColumn, StatsScreen, ProfileSelectScreen
from models import UserProfile


class TypingTutor(App):
    CSS_PATH = "styles.tcss"

    # Added F2 binding for fingers
    BINDINGS = [
        Binding("f1", "toggle_keyboard", "Toggle Keys"),
        Binding("f2", "toggle_fingers", "Toggle Fingers"),
        Binding("f3", "toggle_stats_pref", "Toggle Stats"),
        Binding("f4", "switch_profile", "Switch Profile"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.target_text = random.choice(config.SENTENCES)
        self.typed_text = ""
        self.start_time = None
        self.total_errors = 0
        self.show_stats_pref = config.SHOW_STATS_ON_END
        self.profile = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-grid"):
            yield Static("", id="stats-bar")
            yield Static("", id="typing-area")

            # Keyboard UI with initial visibility check
            kb_classes = "" if config.SHOW_QWERTY else "hidden"
            with Vertical(id="keyboard-section", classes=kb_classes):
                rows = [
                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
                    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
                ]
                for r in rows:
                    with Horizontal(classes="key-row"):
                        for c in r:
                            yield Static(
                                c,
                                classes="key",
                                id=f"key-{config.ID_MAP.get(c, c.lower())}",
                            )

                with Horizontal(classes="key-row"):
                    yield Static("SPACE", id="key-space", classes="key")

            # Finger Guide UI with initial visibility check
            fg_classes = "" if config.SHOW_FINGERS else "hidden"
            with Horizontal(id="finger-guide-wrapper", classes=fg_classes):
                with Horizontal(id="finger-guide"):
                    for fid, dimensions in config.FINGER_HEIGHTS.items():
                        yield FingerColumn(
                            fid, dimensions.height, dimensions.width
                        )  # (h, w)

        yield Footer()

    def on_mount(self) -> None:
        self.action_switch_profile()

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

    def action_switch_profile(self) -> None:
        def set_profile(profile: UserProfile):
            if profile:
                self.profile = profile
                self.apply_profile_config()
                self.notify(f"Welcome, {profile.name}!")
                self.reset_drill()

        self.push_screen(ProfileSelectScreen(), set_profile)

    def action_quit(self) -> None:
        """Saves current UI configuration to the profile before exiting."""
        if self.profile:
            kb_visible = not self.query_one("#keyboard-section").has_class("hidden")
            fg_visible = not self.query_one("#finger-guide-wrapper").has_class("hidden")

            # 2. Update profile overrides
            self.profile.config_overrides.update(
                {
                    "SHOW_QWERTY": kb_visible,
                    "SHOW_FINGERS": fg_visible,
                    "SHOW_STATS_ON_END": self.show_stats_pref,
                }
            )

            # 3. Persist to disk
            self.profile.save()
            self.notify(f"Config saved for {self.profile.name}")

        # 4. Standard exit
        self.exit()

    def on_key(self, event) -> None:
        if self.profile is None:
            return

        if len(self.typed_text) >= len(self.target_text):
            if event.key == "enter":
                self.reset_drill()
            elif event.key == "s":  # Manual trigger for stats
                self.show_final_stats()
            return

        if event.key == "space":
            char = " "
        elif event.is_printable:
            char = event.character
        else:
            char = None

        if not self.start_time and char and len(char) == 1:
            self.start_time = time.time()

        if event.key == "backspace":
            self.typed_text = self.typed_text[:-1]
        elif char and len(char) == 1:
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
        acc = round(
            (
                (len(self.typed_text) - self.total_errors)
                / max(1, len(self.typed_text) + self.total_errors)
            )
            * 100
        )

        self.query_one("#stats-bar").update(
            f"WPM: {wpm} | ACCURACY: {acc}% | ERRORS: {self.total_errors}"
        )

        rich = ""
        for i, c in enumerate(self.target_text):
            if i < len(self.typed_text):
                rich += (
                    f"[#9ece6a]{c}[/]"
                    if self.typed_text[i] == c
                    else f"[#f7768e]{c}[/]"
                )
            elif i == len(self.typed_text):
                rich += f"[reverse]{c}[/]"
            else:
                rich += c
        self.query_one("#typing-area").update(f"\n\n{rich}")

        self.query(".key").remove_class("active-key")
        self.query(".finger-body").remove_class("active-finger")

        if len(self.typed_text) < len(self.target_text):
            nxt = self.target_text[len(self.typed_text)]
            kid = (
                f"#key-{'space' if nxt == ' ' else config.ID_MAP.get(nxt, nxt.lower())}"
            )

            try:
                self.query_one(kid).add_class("active-key")
            except Exception:
                pass

            fid = config.FINGER_MAP.get(nxt)
            if fid:
                try:
                    self.query_one(f"#{fid}").add_class("active-finger")
                except Exception:
                    pass

        if not self.profile:
            self.query_one("#stats-bar").update(
                f"WPM: {wpm} | ACCURACY: {acc}% | [bold red]AWAITING PROFILE...[/]"
            )
        else:
            # Now it is safe to access the profile
            lesson_idx = self.profile.current_lesson_index

            # Ensure index is within LESSONS bounds to prevent IndexErrors
            if lesson_idx < len(config.LESSONS):
                lesson_name = config.LESSONS[lesson_idx]["name"]
            else:
                lesson_name = "Master Mode (Free Typing)"

            self.query_one("#stats-bar").update(
                f"LESSON: {lesson_name} | WPM: {wpm} | ACCURACY: {acc}%"
            )

    def reset_drill(self) -> None:
        """Selects text based on the current lesson stage."""
        if self.profile:
            self.target_text = self.generate_lesson_text()
        else:
            self.target_text = random.choice(config.SENTENCES)

        self.typed_text = ""
        self.start_time = None
        self.total_errors = 0
        self.refresh_display()

    def check_completion(self) -> None:
        if len(self.typed_text) == len(self.target_text):
            self.evaluate_drill()
            if self.show_stats_pref:
                self.show_final_stats()
            else:
                # Prompt user in the typing area
                self.query_one("#typing-area").update(
                    f"\n[#9ece6a]{self.target_text}[/]\n\n"
                    "[reverse] PRESS ENTER FOR NEXT [/]  [#7aa2f7](OR 'S' FOR STATS)[/]"
                )

    def show_final_stats(self) -> None:
        """Only handles the UI modal display."""
        elapsed = (time.time() - self.start_time) / 60
        wpm = round((len(self.typed_text) / 5) / elapsed)
        acc = round(
            (
                (len(self.typed_text) - self.total_errors)
                / max(1, len(self.typed_text) + self.total_errors)
            )
            * 100
        )

        # We don't call evaluate_drill here anymore because it ran in check_completion
        self.push_screen(
            StatsScreen(wpm, acc, self.total_errors), lambda _: self.reset_drill()
        )

    def apply_profile_config(self):
        """Applies the configuration saved in the user's profile."""
        overrides = self.profile.config_overrides
        self.show_stats_pref = overrides.get("SHOW_STATS_ON_END", True)

        # Update UI visibility
        self.query_one("#keyboard-section").set_class(
            not overrides.get("SHOW_QWERTY", True), "hidden"
        )
        self.query_one("#finger-guide-wrapper").set_class(
            not overrides.get("SHOW_FINGERS", True), "hidden"
        )

    def generate_lesson_text(self) -> str:
        """Generates text based on the current lesson type."""
        lesson = config.LESSONS[self.profile.current_lesson_index]
        keys = lesson["keys"]

        if lesson["type"] == "repeat":
            # Example: "ASDFG HJKL; ASDFG HJKL;"
            return (keys + " ") * 3
        else:
            # Example: Scrambled combinations like "ahkk ghkl"
            words = []
            clean_keys = keys.replace(" ", "")
            for _ in range(5):
                word = "".join(random.choices(clean_keys, k=4))
                words.append(word)
            return " ".join(words).upper()

    def evaluate_drill(self) -> bool:
        """Determines if the user passed the requirements and increments lesson index."""
        if not self.start_time:
            return False

        elapsed = (time.time() - self.start_time) / 60
        wpm = round((len(self.typed_text) / 5) / elapsed)
        acc = round(
            (
                (len(self.typed_text) - self.total_errors)
                / max(1, len(self.typed_text) + self.total_errors)
            )
            * 100
        )

        # Check requirements from config
        lesson = config.LESSONS[self.profile.current_lesson_index]
        passed = acc >= lesson["target_acc"] and wpm >= lesson["target_wpm"]

        if passed:
            self.profile.current_lesson_index += 1
            # Prevent overflow if they finish all lessons
            if self.profile.current_lesson_index >= len(config.LESSONS):
                self.profile.current_lesson_index = len(config.LESSONS) - 1

            self.notify(f"LEVEL UP: {lesson['name']} Cleared!")
        else:
            self.notify("Requirements not met. Lesson will repeat.", severity="warning")

        # Update profile records and save
        if wpm > self.profile.wpm_record:
            self.profile.wpm_record = wpm
        self.profile.total_drills += 1
        self.profile.save()

        return passed


if __name__ == "__main__":
    TypingTutor().run()
