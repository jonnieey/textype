"""Main application module for the Textype typing tutor.

This module contains the main TypingTutor application class that orchestrates
the typing practice sessions, UI interactions, and user progress tracking.
"""
import time
import random
from typing import Optional, Dict, List
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual import events
from rich.text import Text

import config
from widgets import FingerColumn, StatsScreen, ProfileSelectScreen
from models import UserProfile
import generator_algorithms as algos
from xkb_resolver import XKBResolver
from keyboard import PhysicalKey, KEYBOARD_ROWS, FINGER_MAP, DISPLAY_MAP, LAYOUT


class TypingTutor(App):
    """Main Textype typing tutor application.

    A Textual-based TUI application for touch typing practice with
    progressive lessons, real-time feedback, and performance tracking.

    Attributes:
        target_text: The text the user should type
        typed_text: The text the user has typed so far
        session_start_time: When the current session started
        session_active: Whether a session is currently in progress
        cumulative_typed_chars: Total characters typed in session
        cumulative_errors: Total errors made in session
        current_chunk_errors: Errors in current text chunk
        chunks_completed: Number of chunks completed in session
        show_stats_pref: Whether to show stats screen automatically
        profile: Current user profile
        resolver: XKB resolver for layout mapping
        target_keys: Physical keys corresponding to target text
        char_to_physical: Mapping from characters to physical keys
    """

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("f1", "toggle_keyboard", "Toggle Keys"),
        Binding("f2", "toggle_fingers", "Toggle Fingers"),
        Binding("f3", "toggle_stats_pref", "Toggle Stats"),
        Binding("f4", "switch_profile", "Switch Profile"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        """Initialize the typing tutor application.

        Sets up session state, XKB resolver, and character-to-physical
        key mapping for the current keyboard layout.
        """
        super().__init__()
        self.target_text = ""
        self.typed_text = ""

        # Session state
        self.session_start_time: Optional[float] = None
        self.session_active: bool = False
        self.cumulative_typed_chars: int = 0
        self.cumulative_errors: int = 0
        self.current_chunk_errors: int = 0
        self.chunks_completed: int = 0  # Track chunks for shuffle logic

        self.show_stats_pref: bool = config.SHOW_STATS_ON_END
        self.profile: Optional[UserProfile] = None
        self.resolver: XKBResolver = XKBResolver()
        self.target_keys: List[PhysicalKey] = []

        # Build Reverse Map: Character -> Physical Key (for validation)
        # Note: This is an approximation. A robust solution might iterate all keycodes.
        self.char_to_physical: Dict[str, PhysicalKey] = {}
        for key in PhysicalKey:
            # Check unmodified
            char = self.resolver.resolve(key.value)
            if char:
                self.char_to_physical[char] = key

            # Check shifted
            self.resolver.update_modifiers(shift=True)
            char_shifted = self.resolver.resolve(key.value)
            if char_shifted:
                self.char_to_physical[char_shifted] = key
            self.resolver.update_modifiers(shift=False)  # Reset

    def compose(self) -> ComposeResult:
        """Compose the main application UI.

        Creates the header, statistics bar, typing area, keyboard visualization,
        finger guide, and footer.

        Yields:
            Widgets for the application UI
        """
        yield Header()
        with Vertical(id="main-grid"):
            yield Static("", id="stats-bar")
            yield Static("", id="typing-area")

            # Keyboard UI with initial visibility check
            kb_classes = "" if config.SHOW_QWERTY else "hidden"

            with Vertical(id="keyboard-section", classes=kb_classes):
                for row in KEYBOARD_ROWS:
                    with Horizontal(classes="key-row"):
                        for key in row:
                            # 1. Check explicit display map
                            if key in DISPLAY_MAP:
                                label = DISPLAY_MAP[key]
                                special_class = (
                                    " special-key"  # Add extra styling class if needed
                                )
                            else:
                                # 2. Resolve via XKB
                                # Note: self.resolver is available here? No, 'self' is the App instance.
                                # compose() is an instance method, so yes.
                                label = self.resolver.resolve(key.value) or ""
                                # If label is a control char (like \x1b), fallback to name
                                if label and (ord(label[0]) < 32):
                                    label = key.name.replace("KEY_", "")
                                special_class = ""

                            # Upper case for consistency
                            if len(label) == 1:
                                label = label.upper()

                            yield Static(
                                label,
                                classes=f"key{special_class}",
                                id=f"key-{key.name}",
                            )

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
        """Initialize the application after mounting.

        Shows the profile selection screen and starts the timer update interval.
        """
        self.action_switch_profile()
        self.set_interval(0.5, self.update_timer)

    def update_timer(self) -> None:
        """Update the session timer and check for session completion.

        Called every 0.5 seconds to update the display and end the session
        when the drill duration is reached.
        """
        if self.session_active and self.session_start_time:
            elapsed = time.time() - self.session_start_time
            if elapsed >= config.DRILL_DURATION:
                self.end_drill_session()
            else:
                self.refresh_display()

    # Toggles for UI elements
    def action_toggle_keyboard(self) -> None:
        """Toggle keyboard visualization visibility.

        Bound to F1 key.
        """
        self.query_one("#keyboard-section").toggle_class("hidden")

    def action_toggle_fingers(self) -> None:
        """Toggle finger guide visualization visibility.

        Bound to F2 key.
        """
        self.query_one("#finger-guide-wrapper").toggle_class("hidden")

    def action_toggle_stats_pref(self) -> None:
        """Toggle whether stats show automatically at the end.

        Bound to F3 key.
        """
        self.show_stats_pref = not self.show_stats_pref
        status = "ON" if self.show_stats_pref else "OFF"
        self.notify(f"Auto-Stats: {status}")

    def action_switch_profile(self) -> None:
        """Switch or create a user profile.

        Bound to F4 key. Shows the profile selection screen.
        """

        def set_profile(profile: UserProfile):
            if profile:
                self.profile = profile
                self.apply_profile_config()
                self.notify(f"Welcome, {profile.name}!")
                self.start_new_session()

        self.push_screen(ProfileSelectScreen(), set_profile)

    def action_quit(self) -> None:
        """Save configuration and exit the application.

        Bound to Escape key. Saves current UI configuration to the
        profile before exiting.
        """
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

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard input during typing practice.

        Processes key presses for typing validation, navigation, and
        session control.

        Args:
            event: Key event from Textual
        """
        if self.profile is None:
            return

        if not self.session_active:
            if event.key == "enter":
                self.start_new_session()
            return

        if len(self.typed_text) >= len(self.target_text):
            # Allow 'enter' or 's' to proceed only if finished
            if event.key == "enter":
                self.load_next_chunk()
            elif event.key == "s":
                self.end_drill_session()
            return

        # Handle Backspace
        if event.key == "backspace":
            self.typed_text = self.typed_text[:-1]
            self.refresh_display()
            return

        # 1. Identify which character was typed
        if event.key == "space":
            char = " "
        elif event.is_printable:
            char = event.character
        else:
            return

        # 2. Determine which PhysicalKey this corresponds to
        if char == " ":
            physical_pressed = PhysicalKey.KEY_SPACE
        else:
            physical_pressed = self.char_to_physical.get(char)
            # Fallback: if we can't map it (e.g. complex compose), rely on char match?
            # ideally physical_pressed shouldn't be None if it's in our map.

        # 3. Check against expected PhysicalKey
        idx = len(self.typed_text)
        if idx < len(self.target_keys):
            expected_physical = self.target_keys[idx]

            # Validation Logic:
            # Check physical key AND character match to ensure correct modifiers (Shift)
            is_correct = False
            physical_match = physical_pressed and physical_pressed == expected_physical
            char_match = char == self.target_text[idx]

            if physical_pressed:
                # If we know the physical key, it must match expected AND produce correct char
                if physical_match and char_match:
                    is_correct = True
            elif char_match:
                # Fallback for unmapped keys
                is_correct = True

            if not self.session_start_time:
                self.session_start_time = time.time()

            if is_correct:
                self.typed_text += char  # Add the *actual* char typed
            else:
                self.current_chunk_errors += 1
                if not config.HARD_MODE:
                    self.typed_text += char

        self.refresh_display()
        self.check_chunk_completion()

    def refresh_display(self) -> None:
        """Refresh the UI with current session state.

        Updates the statistics bar, typing area highlighting, and
        visual feedback for the current key and finger.
        """
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

        # Highlighting logic
        rich_text = Text("")
        for i, c in enumerate(self.target_text):
            if i < len(self.typed_text):
                style = "#9ece6a" if self.typed_text[i] == c else "#f7768e"
                rich_text.append(c, style=style)
            elif i == len(self.typed_text):
                rich_text.append(c, style="reverse")
            else:
                rich_text.append(c)

        self.query_one("#typing-area").update(rich_text)

        self.query(".key").remove_class("active-key")
        self.query(".finger-body").remove_class("active-finger")

        if len(self.typed_text) < len(self.target_keys):
            physical_key = self.target_keys[len(self.typed_text)]

            # Highlight finger
            fid = FINGER_MAP.get(physical_key)
            if fid:
                try:
                    self.query_one(f"#{fid}").add_class("active-finger")
                except Exception:
                    pass

            # Highlight keyboard key
            try:
                self.query_one(f"#key-{physical_key.name}").add_class("active-key")
            except Exception:
                pass

            # Highlight Shift if needed
            # We need to know if the TARGET character requires shift on THIS layout.
            # We resolve the key without shift, and with shift.
            self.resolver.update_modifiers(shift=False)
            base_char = self.resolver.resolve(physical_key.value)

            self.resolver.update_modifiers(shift=True)
            shifted_char = self.resolver.resolve(physical_key.value)
            self.resolver.update_modifiers(shift=False)  # Reset

            target_char = self.target_text[len(self.typed_text)]

            # If the target char matches the shifted version but NOT the base version, we need shift.
            if target_char == shifted_char and target_char != base_char:
                # Determine which shift (left or right) based on hand
                # If key is Left hand (L1-L4), use Right Shift.
                # If key is Right hand (R1-R4), use Left Shift.
                if fid:
                    shift_id = (
                        f"#key-{PhysicalKey.KEY_SHIFT_RIGHT.name}"
                        if fid.startswith("L")
                        else f"#key-{PhysicalKey.KEY_SHIFT_LEFT.name}"
                    )
                    try:
                        self.query_one(shift_id).add_class("active-key")
                    except Exception:
                        pass

    def start_new_session(self) -> None:
        """Start a new 5-minute drill session.

        Resets session state and generates new practice text based on
        the current lesson or default sentences.
        """
        self.session_active = True
        self.session_start_time = None
        self.cumulative_typed_chars = 0
        self.cumulative_errors = 0
        self.current_chunk_errors = 0
        self.chunks_completed = 0

        if self.profile:
            self.target_text = self.generate_lesson_text()
        else:
            self.target_text = random.choice(config.SENTENCES)

        self.typed_text = ""
        self.refresh_display()

    def load_next_chunk(self) -> None:
        """Load the next chunk of text within the same session.

        Updates cumulative statistics and generates new practice text
        when the current chunk is completed.
        """
        self.cumulative_typed_chars += len(self.typed_text)
        self.cumulative_errors += self.current_chunk_errors
        self.chunks_completed += 1

        if self.profile:
            self.target_text = self.generate_lesson_text()
        else:
            self.target_text = random.choice(config.SENTENCES)

        self.typed_text = ""
        self.current_chunk_errors = 0
        self.refresh_display()

    def check_chunk_completion(self) -> None:
        """Check if the current text chunk has been completed.

        Automatically loads the next chunk if the session is still active.
        """
        if len(self.typed_text) == len(self.target_text):
            # If session is still active, load next chunk
            if self.session_active:
                self.load_next_chunk()

    def end_drill_session(self) -> None:
        """End the current session and show statistics.

        Stops the session timer and evaluates performance against
        lesson requirements.
        """
        self.session_active = False

        # Add final stats
        self.cumulative_typed_chars += len(self.typed_text)
        self.cumulative_errors += self.current_chunk_errors

        self.evaluate_drill_and_show_stats()

    def evaluate_drill_and_show_stats(self) -> None:
        """Evaluate drill performance and show results.

        Calculates final WPM and accuracy, checks if lesson requirements
        are met, updates user progress, and shows statistics screen.
        """
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

    def apply_profile_config(self) -> None:
        """Apply the configuration saved in the user's profile.

        Updates UI visibility and preferences based on profile overrides.
        """
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
        """Generate practice text for the current lesson.

        Selects the appropriate algorithm based on lesson configuration
        and generates a sequence of physical keys, then converts them
        to characters using the current keyboard layout.

        Returns:
            String of characters to type for the current lesson

        Raises:
            KeyError: If row_key is not found in LAYOUT
        """
        lesson = config.LESSONS[self.profile.current_lesson_index]
        algo_type = lesson.get("algo")
        row_key = lesson.get("row", "home")
        row_data = LAYOUT.get(row_key)

        should_shuffle = self.chunks_completed >= config.SHUFFLE_AFTER

        dispatch = {
            "repeat": lambda: algos.single_key_repeat(
                row_data["left"] + row_data["right"],
                shuffle=should_shuffle,
            ),
            "adjacent": lambda: algos.same_hand_adjacent(
                row_data,
                shuffle=should_shuffle,
            ),
            "alternating": lambda: algos.alternating_pairs(
                row_data,
                shuffle=should_shuffle,
            ),
            "mirror": lambda: algos.mirror_pairs(
                row_data,
                shuffle=should_shuffle,
            ),
            "rolls": lambda: algos.rolls(
                row_data,
                shuffle=should_shuffle,
            ),
            "pseudo": lambda: algos.pseudo_words(row_data),
        }

        generator = dispatch.get(algo_type)
        if generator:
            physical_keys = generator()
        else:
            all_keys = row_data["left"] + row_data["right"]
            physical_keys = [random.choice(all_keys) for _ in range(40)]

        self.target_keys = physical_keys
        shift_mode = lesson.get("shift_mode", "off")

        # 🔤 Render via XKB
        rendered = []
        for key in physical_keys:
            if key == PhysicalKey.KEY_SPACE:
                rendered.append(" ")
                continue

            use_shift = False
            if shift_mode == "always":
                use_shift = True
            elif shift_mode == "mixed":
                use_shift = random.choice([True, False])

            self.resolver.update_modifiers(shift=use_shift)
            char = self.resolver.resolve(key.value)

            # Fallback if shift produced nothing (unlikely for standard keys)
            if not char and use_shift:
                self.resolver.update_modifiers(shift=False)
                char = self.resolver.resolve(key.value)

            rendered.append(char or "")

        return "".join(rendered)


if __name__ == "__main__":
    TypingTutor().run()
