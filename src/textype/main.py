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
import generator_algorithms as algos


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
        self.target_text = ""
        self.typed_text = ""

        # Session state
        self.session_start_time = None
        self.session_active = False
        self.cumulative_typed_chars = 0
        self.cumulative_errors = 0
        self.current_chunk_errors = 0

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
                # Row 1
                with Horizontal(classes="key-row"):
                    for c in ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]:
                        yield Static(
                            c,
                            classes="key",
                            id=f"key-{config.ID_MAP.get(c, c.lower())}",
                        )
                # Row 2
                with Horizontal(classes="key-row"):
                    for c in ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"]:
                        yield Static(
                            c,
                            classes="key",
                            id=f"key-{config.ID_MAP.get(c, c.lower())}",
                        )
                # Row 3
                with Horizontal(classes="key-row"):
                    yield Static("SHIFT", classes="key special-key", id="key-shift-l")
                    for c in ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]:
                        yield Static(
                            c,
                            classes="key",
                            id=f"key-{config.ID_MAP.get(c, c.lower())}",
                        )
                    yield Static("SHIFT", classes="key special-key", id="key-shift-r")

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
        self.set_interval(0.5, self.update_timer)

    def update_timer(self) -> None:
        if self.session_active and self.session_start_time:
            elapsed = time.time() - self.session_start_time
            if elapsed >= config.DRILL_DURATION:
                self.end_drill_session()
            else:
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

    def action_switch_profile(self) -> None:
        def set_profile(profile: UserProfile):
            if profile:
                self.profile = profile
                self.apply_profile_config()
                self.notify(f"Welcome, {profile.name}!")
                self.start_new_session()

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

        # If session is inactive, allow Enter to restart
        if not self.session_active:
            if event.key == "enter":
                self.start_new_session()
            return

        if len(self.typed_text) >= len(self.target_text):
            # This shouldn't happen often with auto-paging, but as a fallback
            if event.key == "enter":
                self.load_next_chunk()
            elif event.key == "s":
                self.end_drill_session()
            return

        if event.key == "space":
            char = " "
        elif event.is_printable:
            char = event.character
        else:
            char = None

        if not self.session_start_time and char:
            self.session_start_time = time.time()

        if event.key == "backspace":
            self.typed_text = self.typed_text[:-1]
        elif char and len(char) == 1:
            idx = len(self.typed_text)
            if idx < len(self.target_text):
                if char == self.target_text[idx]:
                    self.typed_text += char
                else:
                    self.current_chunk_errors += 1
                    if not config.HARD_MODE:
                        self.typed_text += char

        self.refresh_display()
        self.check_chunk_completion()

    def refresh_display(self) -> None:
        # Time Calculation
        if self.session_start_time and self.session_active:
            elapsed = time.time() - self.session_start_time
            remaining = max(0, config.DRILL_DURATION - elapsed)
        else:
            elapsed = 0
            remaining = config.DRILL_DURATION

        mins, secs = divmod(int(remaining), 60)
        timer_str = f"{mins:02}:{secs:02}"

        # Stats Calculation
        total_chars = self.cumulative_typed_chars + len(self.typed_text)
        total_errs = self.cumulative_errors + self.current_chunk_errors

        # Avoid division by zero
        safe_elapsed = elapsed if elapsed > 0 else 1e-6
        wpm = round((total_chars / 5) / (safe_elapsed / 60)) if elapsed > 0 else 0

        acc = round(
            ((total_chars - total_errs) / max(1, total_chars + total_errs)) * 100
        )

        # Update Header
        if self.profile:
            lesson_idx = self.profile.current_lesson_index
            if lesson_idx < len(config.LESSONS):
                lesson_name = config.LESSONS[lesson_idx]["name"]
            else:
                lesson_name = "Master Mode"

            status_text = (
                f"LESSON: {lesson_name} | TIME: {timer_str} | WPM: {wpm} | ACC: {acc}%"
            )
        else:
            status_text = f"TIME: {timer_str} | WPM: {wpm} | ACC: {acc}% | [bold red]AWAITING PROFILE...[/]"

        self.query_one("#stats-bar").update(status_text)

        # Highlighting logic (same as before)
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
            key_lookup = nxt.lower()
            kid_suffix = config.ID_MAP.get(key_lookup, key_lookup)
            kid = f"#key-{kid_suffix}"

            try:
                self.query_one(kid).add_class("active-key")
            except Exception:
                pass

            fid = config.FINGER_MAP.get(nxt.upper())
            if nxt.isupper() and fid:
                shift_id = "#key-shift-r" if fid.startswith("L") else "#key-shift-l"
                try:
                    self.query_one(shift_id).add_class("active-key")
                except Exception:
                    pass

            if fid:
                try:
                    self.query_one(f"#{fid}").add_class("active-finger")
                except Exception:
                    pass

    def start_new_session(self) -> None:
        """Starts a new 5-minute drill session."""
        self.session_active = True
        self.session_start_time = None
        self.cumulative_typed_chars = 0
        self.cumulative_errors = 0
        self.current_chunk_errors = 0

        if self.profile:
            self.target_text = self.generate_lesson_text()
        else:
            self.target_text = random.choice(config.SENTENCES)

        self.typed_text = ""
        self.refresh_display()

    def load_next_chunk(self) -> None:
        """Loads the next chunk of text within the same session."""
        self.cumulative_typed_chars += len(self.typed_text)
        self.cumulative_errors += self.current_chunk_errors

        if self.profile:
            self.target_text = self.generate_lesson_text()
        else:
            self.target_text = random.choice(config.SENTENCES)

        self.typed_text = ""
        self.current_chunk_errors = 0
        self.refresh_display()

    def check_chunk_completion(self) -> None:
        if len(self.typed_text) == len(self.target_text):
            # If session is still active, load next chunk
            if self.session_active:
                self.load_next_chunk()

    def end_drill_session(self) -> None:
        """Ends the session and shows stats."""
        self.session_active = False

        # Add final stats
        self.cumulative_typed_chars += len(self.typed_text)
        self.cumulative_errors += self.current_chunk_errors

        self.evaluate_drill_and_show_stats()

    def evaluate_drill_and_show_stats(self) -> None:
        # Calculate final stats
        elapsed = config.DRILL_DURATION / 60  # Normalized to full duration

        wpm = round((self.cumulative_typed_chars / 5) / elapsed)
        total_ops = self.cumulative_typed_chars + self.cumulative_errors
        acc = round(
            ((self.cumulative_typed_chars - self.cumulative_errors) / max(1, total_ops))
            * 100
        )

        passed = False
        if self.profile:
            lesson = config.LESSONS[self.profile.current_lesson_index]
            passed = acc >= lesson["target_acc"] and wpm >= lesson["target_wpm"]

            if passed:
                self.profile.current_lesson_index += 1
                if self.profile.current_lesson_index >= len(config.LESSONS):
                    self.profile.current_lesson_index = len(config.LESSONS) - 1
                self.notify(f"LEVEL UP: {lesson['name']} Cleared!")
            else:
                self.notify(
                    "Requirements not met. Lesson will repeat.", severity="warning"
                )

            if wpm > self.profile.wpm_record:
                self.profile.wpm_record = wpm
            self.profile.total_drills += 1
            self.profile.save()

        if self.show_stats_pref:
            self.push_screen(
                StatsScreen(wpm, acc, self.cumulative_errors),
                lambda _: self.start_new_session(),
            )
        else:
            self.query_one("#typing-area").update(
                f"\n[#9ece6a]SESSION COMPLETE[/]\n\n"
                f"WPM: {wpm} | ACC: {acc}% | ERRORS: {self.cumulative_errors}\n\n"
                "[reverse] PRESS ENTER TO START NEXT SESSION [/]"
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
        lesson = config.LESSONS[self.profile.current_lesson_index]
        algo_type = lesson.get("algo")
        row_key = lesson.get("row", "home")
        row_data = algos.LAYOUT.get(row_key)

        dispatch = {
            "repeat": lambda: algos.single_key_repeat(
                row_data["left"] + row_data["right"]
            ),
            "adjacent": lambda: algos.same_hand_adjacent(row_data),
            "alternating": lambda: algos.alternating_pairs(row_data),
            "mirror": lambda: algos.mirror_pairs(row_data),
            "rolls": lambda: algos.rolls(row_data),
            "pseudo": lambda: algos.pseudo_words(row_data),
        }

        # Execute the mapped function or fallback to a basic scramble
        generator = dispatch.get(algo_type)
        if generator:
            return generator()

        all_keys = row_data["left"] + row_data["right"]
        return " ".join(["".join(random.choices(all_keys, k=4)) for _ in range(10)])


if __name__ == "__main__":
    TypingTutor().run()
