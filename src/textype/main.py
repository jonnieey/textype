"""Main application module for the Textype typing tutor.

This module contains the main TypingTutor application class that orchestrates
the typing practice sessions, UI interactions, and user progress tracking.
"""
import asyncio
import time
import random
from typing import Optional, Dict, List, Tuple, Any
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual import events
from rich.text import Text

import textype.code_generator as code_generator
import textype.config as config
import textype.algorithms_generator as algos

from textype.curriculum import LESSONS
from textype.keyboard import PhysicalKey, KEYBOARD_ROWS, FINGER_MAP, DISPLAY_MAP, LAYOUT
from textype.models import UserProfile, FINGER_HEIGHTS
from textype.sentence_generator import generate_sentence, generate_sentence_async
from textype.widgets import (
    FingerColumn,
    StatsScreen,
    ProfileSelectScreen,
    ProfileInfoScreen,
)
from textype.xkb_resolver import XKBResolver


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
        Binding("f5", "show_profile", "Profile Info"),
        Binding("f6", "toggle_practice_mode", "Practice Mode"),
        Binding("ctrl+q", "quit", "Quit"),
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

        self.profile: Optional[UserProfile] = None
        self.show_stats_pref: bool = self._get_config("SHOW_STATS_ON_END")
        self.resolver: XKBResolver = XKBResolver()
        self.target_keys: List[PhysicalKey] = []
        self.last_drill_passed: bool = False
        self.previous_lesson_index: int = 0
        self.current_code_language: Optional[str] = None

        # Async pre-fetching state
        self._prefetch_task: Optional[asyncio.Task] = None
        self._prefetched_text: Optional[str] = None
        self._prefetched_keys: Optional[List[PhysicalKey]] = None
        self._prefetched_language: Optional[str] = None
        self._prefetched_mode: Optional[str] = None  # "curriculum", "sentences", "code"

        # Build Reverse Map: Character -> Physical Key (for validation)
        # Note: This is an approximation. A robust solution might iterate all keycodes.
        self.char_to_physical: Dict[
            str, PhysicalKey
        ] = self._build_char_to_physical_map()

        # Cache for shift detection results
        self._key_char_cache: Dict[
            PhysicalKey, Tuple[Optional[str], Optional[str]]
        ] = {}

        # Cache for keyboard key labels
        self._key_label_cache: Dict[PhysicalKey, str] = self._build_key_label_cache()

    def _get_config(self, key: str) -> Any:
        """Get configuration value from profile or fallback to default."""
        if self.profile:
            return self.profile.get_config(key)
        else:
            return getattr(config, key)

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
            kb_classes = "" if self._get_config("SHOW_QWERTY") else "hidden"

            with Vertical(id="keyboard-section", classes=kb_classes):
                for row in KEYBOARD_ROWS:
                    with Horizontal(classes="key-row"):
                        for key in row:
                            # Use cached label
                            label = self._key_label_cache.get(key, "")
                            special_class = " special-key" if key in DISPLAY_MAP else ""

                            yield Static(
                                label,
                                classes=f"key{special_class}",
                                id=f"key-{key.name}",
                            )

            # Finger Guide UI with initial visibility check
            fg_classes = "" if self._get_config("SHOW_FINGERS") else "hidden"
            with Horizontal(id="finger-guide-wrapper", classes=fg_classes):
                with Horizontal(id="finger-guide"):
                    for fid, dimensions in FINGER_HEIGHTS.items():
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
            if elapsed >= self._get_config("DRILL_DURATION"):
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

    def action_toggle_practice_mode(self) -> None:
        """Toggle between curriculum, sentence, and code practice mode.

        Bound to F6 key.
        """
        if not self.profile:
            self.notify(
                "No active profile. Use F4 to select or create a profile.",
                severity="warning",
            )
            return

        current_mode = self.profile.config_overrides.get("PRACTICE_MODE", "curriculum")
        if current_mode == "curriculum":
            new_mode = "sentences"
        elif current_mode == "sentences":
            new_mode = "code"
        else:
            new_mode = "curriculum"
        self.profile.config_overrides["PRACTICE_MODE"] = new_mode
        self.profile.save()

        if new_mode == "sentences":
            status = "Sentence Practice"
        elif new_mode == "code":
            status = "Code Practice"
        else:
            status = "Curriculum"
        self.notify(f"Practice Mode: {status}")

        # Restart session with new mode
        if self.session_active:
            self._reset_for_mode_change()
        else:
            self.start_new_session()

    def _reset_for_mode_change(self) -> None:
        """Reset typing state for practice mode change without evaluating current drill.

        Keeps session active and timer running, but resets text and statistics.
        """
        # Cancel any pending pre-fetch for the old mode
        self._cancel_prefetch()

        # Reset typing state
        self.cumulative_typed_chars = 0
        self.cumulative_errors = 0
        self.current_chunk_errors = 0
        self.chunks_completed = 0
        self.typed_text = ""

        # Generate new practice text and keys
        self.target_text = self._get_practice_text()

        # Cancel any pending pre-fetch for the old mode
        self._cancel_prefetch()

        # Reset typing state
        self.cumulative_typed_chars = 0
        self.cumulative_errors = 0
        self.current_chunk_errors = 0
        self.chunks_completed = 0
        self.typed_text = ""

        # Generate new practice text and keys
        self.target_text = self._get_practice_text()

        # Refresh display
        self.refresh_display()

    def action_switch_profile(self) -> None:
        """Switch or create a user profile.

        Bound to F4 key. Shows the profile selection screen.
        """

        def set_profile(profile: UserProfile):
            if profile:
                # Cancel any existing pre-fetch from previous profile
                self._cancel_prefetch()
                self.profile = profile
                self.apply_profile_config()
                self.notify(f"Welcome, {profile.name}!")
                self.start_new_session()

        self.push_screen(ProfileSelectScreen(), set_profile)

    def action_show_profile(self) -> None:
        """Show current profile information and management options.

        Bound to f5 key. Shows profile info screen.
        """
        if not self.profile:
            self.notify(
                "No active profile. Use F4 to select or create a profile.",
                severity="warning",
            )
            return

        # Store current practice mode to detect changes
        old_practice_mode = self.profile.config_overrides.get(
            "PRACTICE_MODE", "curriculum"
        )

        def handle_result(result: tuple):
            action, name = result
            if action == "delete":
                # Delete the profile
                deleted = UserProfile.delete(name)
                if deleted:
                    self.notify(f"Profile '{name}' deleted.")
                    if self.profile and self.profile.name == name:
                        self.profile = None
                        self.notify(
                            "Current profile cleared. Please select a new profile."
                        )
                        # Automatically show profile selection screen
                        self.action_switch_profile()
                else:
                    self.notify(f"Failed to delete profile '{name}'.", severity="error")
            elif action == "saved":
                # Configuration saved, apply changes
                self.apply_profile_config()
                self.notify(f"Profile configuration saved for {name}")

                # Check if practice mode changed and restart session if needed
                new_practice_mode = self.profile.config_overrides.get(
                    "PRACTICE_MODE", "curriculum"
                )
                if new_practice_mode != old_practice_mode:
                    if self.session_active:
                        self._reset_for_mode_change()
                    else:
                        self.start_new_session()
            # cancelled or other actions just return

        self.push_screen(ProfileInfoScreen(self.profile), handle_result)

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

        # Cancel any pending pre-fetch tasks
        self._cancel_prefetch()

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
            elif event.key == "r":
                self.repeat_lesson()
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
        elif event.key == "enter":
            char = "\n"
        elif event.key == "tab":
            char = "\t"
        elif event.is_printable:
            char = event.character
        else:
            return

        # 2. Determine which PhysicalKey this corresponds to
        if char == " ":
            physical_pressed = PhysicalKey.KEY_SPACE
        elif char == "\n" or char == "\r":
            physical_pressed = PhysicalKey.KEY_ENTER
        elif char == "\t":
            physical_pressed = PhysicalKey.KEY_TAB
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
            target_char = self.target_text[idx]
            char_match = char == target_char
            # Special case: Enter key matches both newline and carriage return
            if (
                physical_pressed == PhysicalKey.KEY_ENTER
                and char in ("\n", "\r")
                and target_char in ("\n", "\r")
            ):
                char_match = True

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
                if not self._get_config("HARD_MODE"):
                    self.typed_text += char

        self.refresh_display()
        self.check_chunk_completion()

    def refresh_display(self) -> None:
        """Refresh the UI with current session state.

        Updates the statistics bar, typing area highlighting, and
        visual feedback for the current key and finger.
        """
        # Calculate time and statistics
        elapsed, remaining = self._calculate_session_time()
        timer_str = self._format_timer(remaining)
        wpm, acc = self._calculate_statistics(elapsed)

        # Update header with mode information
        status_text = self._build_status_text(timer_str, wpm, acc)
        self.query_one("#stats-bar").update(status_text)

        # Update typing area with highlighting
        self._update_typing_area()

        # Highlight current key and finger
        self._highlight_current_key_and_finger()

    def _calculate_session_time(self) -> Tuple[float, float]:
        """Calculate elapsed and remaining session time.

        Returns:
            Tuple of (elapsed_time, remaining_time) in seconds
        """
        if self.session_start_time and self.session_active:
            elapsed = time.time() - self.session_start_time
            remaining = max(0, self._get_config("DRILL_DURATION") - elapsed)
        else:
            elapsed = 0
            remaining = self._get_config("DRILL_DURATION")
        return elapsed, remaining

    def _format_timer(self, remaining: float) -> str:
        """Format remaining time as MM:SS string.

        Args:
            remaining: Remaining time in seconds

        Returns:
            Formatted timer string (MM:SS)
        """
        mins, secs = divmod(int(remaining), 60)
        return f"{mins:02}:{secs:02}"

    def _calculate_statistics(self, elapsed: float) -> Tuple[int, int]:
        """Calculate typing statistics.

        Args:
            elapsed: Elapsed time in seconds

        Returns:
            Tuple of (WPM, accuracy_percentage)
        """
        total_chars = self.cumulative_typed_chars + len(self.typed_text)
        total_errs = self.cumulative_errors + self.current_chunk_errors

        # Avoid division by zero
        safe_elapsed = elapsed if elapsed > 0 else 1e-6
        wpm = round((total_chars / 5) / (safe_elapsed / 60)) if elapsed > 0 else 0

        acc = round(
            ((total_chars - total_errs) / max(1, total_chars + total_errs)) * 100
        )
        return wpm, acc

    def _build_status_text(self, timer_str: str, wpm: int, acc: int) -> str:
        """Build the status text for the stats bar.

        Args:
            timer_str: Formatted timer string
            wpm: Words per minute
            acc: Accuracy percentage

        Returns:
            Status text string
        """
        if not self.profile:
            return f"TIME: {timer_str} | WPM: {wpm} | ACC: {acc}% | [bold red]AWAITING PROFILE...[/]"

        mode_display = self._get_mode_display()
        return f"MODE: {mode_display} | TIME: {timer_str} | WPM: {wpm} | ACC: {acc}%"

    def _get_mode_display(self) -> str:
        """Get the display string for the current practice mode.

        Returns:
            Mode display string
        """
        practice_mode = self.profile.config_overrides.get("PRACTICE_MODE", "curriculum")

        if practice_mode == "sentences":
            mode_display = "SENTENCE PRACTICE"
            source = self._get_config("SENTENCE_SOURCE")
            if source:
                mode_display = f"{mode_display} ({source.upper()})"
        elif practice_mode == "code":
            if self.current_code_language:
                mode_display = f"CODE ({self.current_code_language.upper()})"
            else:
                mode_display = "CODE PRACTICE"
            source = self._get_config("CODE_SOURCE")
            if source:
                mode_display = f"{mode_display} ({source.upper()})"
        else:
            lesson_idx = self.profile.current_lesson_index
            if lesson_idx < len(LESSONS):
                mode_display = LESSONS[lesson_idx]["name"]
            else:
                mode_display = "Master Mode"

        return mode_display

    def _update_typing_area(self) -> None:
        """Update the typing area with highlighting for typed vs target text."""
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

    def _highlight_current_key_and_finger(self) -> None:
        """Highlight the current key and finger in the UI."""
        self.query(".key").remove_class("active-key")
        self.query(".finger-body").remove_class("active-finger")

        if len(self.typed_text) >= len(self.target_keys):
            return

        physical_key = self.target_keys[len(self.typed_text)]
        self._highlight_finger(physical_key)
        self._highlight_keyboard_key(physical_key)
        self._highlight_shift_if_needed(physical_key)

    def _highlight_finger(self, physical_key: PhysicalKey) -> None:
        """Highlight the finger corresponding to the current key.

        Args:
            physical_key: The current physical key
        """
        fid = FINGER_MAP.get(physical_key)
        if fid:
            try:
                self.query_one(f"#{fid}").add_class("active-finger")
            except Exception:
                pass

    def _highlight_keyboard_key(self, physical_key: PhysicalKey) -> None:
        """Highlight the keyboard key in the UI.

        Args:
            physical_key: The current physical key
        """
        try:
            self.query_one(f"#key-{physical_key.name}").add_class("active-key")
        except Exception:
            pass

    def _highlight_shift_if_needed(self, physical_key: PhysicalKey) -> None:
        """Highlight shift keys if the current character requires shift.

        Args:
            physical_key: The current physical key
        """
        target_char = self.target_text[len(self.typed_text)]
        base_char, shifted_char = self._get_key_characters(physical_key)

        # If the target char matches the shifted version but NOT the base version, we need shift.
        if target_char == shifted_char and target_char != base_char:
            fid = FINGER_MAP.get(physical_key)

            # Determine which shift (left or right) based on hand
            # If key is Left hand (L1-L4), use Right Shift.
            # If key is Right hand (R1-R4), use Left Shift.
            if fid:
                shift_id = (
                    f"#key-{PhysicalKey.KEY_SHIFT_RIGHT.name}"
                    if fid.startswith("L")
                    else f"#key-{PhysicalKey.KEY_SHIFT_LEFT.name}"
                )
                # Highlight shift key on keyboard
                try:
                    self.query_one(shift_id).add_class("active-key")
                except Exception:
                    pass

                # Highlight shift finger on finger guide
                shift_finger = "R4" if fid.startswith("L") else "L1"
                try:
                    self.query_one(f"#{shift_finger}").add_class("active-finger")
                except Exception:
                    pass

    def _get_key_characters(
        self, physical_key: PhysicalKey
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get the base and shifted characters for a physical key.

        Uses caching to avoid repeated XKB resolver calls.

        Args:
            physical_key: The physical key to check

        Returns:
            Tuple of (base_character, shifted_character)
        """
        # Check cache first
        if physical_key in self._key_char_cache:
            return self._key_char_cache[physical_key]

        # Resolve characters
        self.resolver.update_modifiers(shift=False)
        base_char = self.resolver.resolve(physical_key.value)

        self.resolver.update_modifiers(shift=True)
        shifted_char = self.resolver.resolve(physical_key.value)
        self.resolver.update_modifiers(shift=False)  # Reset

        # Cache the result
        result = (base_char, shifted_char)
        self._key_char_cache[physical_key] = result

        return result

    def _get_practice_text(self) -> str:
        """Get practice text based on current profile and practice mode.

        Also sets self.target_keys for the generated text.

        Returns:
            Text to practice (lesson, sentences, or code snippets)
        """
        # Reset current code language (will be set if in code mode)
        self.current_code_language = None

        # Check if we have pre-fetched content for the current mode
        if self.profile:
            practice_mode = self.profile.config_overrides.get(
                "PRACTICE_MODE", "curriculum"
            )
            if (
                self._prefetched_text is not None
                and self._prefetched_mode == practice_mode
            ):
                # Use pre-fetched content
                text = self._prefetched_text
                keys = self._prefetched_keys
                language = self._prefetched_language

                # Clear pre-fetched data (we're consuming it)
                self._prefetched_text = None
                self._prefetched_keys = None
                self._prefetched_language = None
                self._prefetched_mode = None

                # Set target keys and language
                self.target_keys = keys
                if language:
                    self.current_code_language = language

                # Start pre-fetching the next chunk in background
                self._start_prefetching()

                return text

        # No pre-fetched content available, generate synchronously
        if not self.profile:
            sentence = generate_sentence(None)
            self.target_keys = self._sentence_to_physical_keys(sentence)
            # Start pre-fetching for future (once profile is selected)
            return sentence

        practice_mode = self.profile.config_overrides.get("PRACTICE_MODE", "curriculum")
        if practice_mode == "sentences":
            sentence = generate_sentence(self.profile.config)
            self.target_keys = self._sentence_to_physical_keys(sentence)
            # Start pre-fetching next chunk
            self._start_prefetching()
            return sentence
        elif practice_mode == "code":
            # Get configured languages, fallback to all supported
            lang_config = self.profile.config_overrides.get(
                "CODE_LANGUAGES", "python,rust,c,cpp"
            )
            allowed_languages = self._parse_language_config(lang_config)

            if not allowed_languages:
                # Fallback to all supported languages if config is empty
                allowed_languages = ["python", "rust", "c", "cpp"]

            language = random.choice(allowed_languages)
            snippet = code_generator.generate_code_snippet(
                language, self.profile.config
            )
            self.target_keys = self._sentence_to_physical_keys(snippet)
            self.current_code_language = language
            # Start pre-fetching next chunk
            self._start_prefetching()
            return snippet
        else:
            # generate_lesson_text() already sets self.target_keys
            # Curriculum mode doesn't need pre-fetching (fast generation)
            return self.generate_lesson_text()

    def _cancel_prefetch(self) -> None:
        """Cancel any pending pre-fetch task and clear pre-fetched data."""
        if self._prefetch_task and not self._prefetch_task.done():
            self._prefetch_task.cancel()
            self._prefetch_task = None
        self._prefetched_text = None
        self._prefetched_keys = None
        self._prefetched_language = None
        self._prefetched_mode = None

    async def _prefetch_next_chunk(self) -> None:
        """Asynchronously pre-fetch the next chunk of practice text based on current mode."""
        # Determine current practice mode and parameters
        if not self.profile:
            # No profile yet, cannot pre-fetch
            return

        practice_mode = self.profile.config_overrides.get("PRACTICE_MODE", "curriculum")

        # Cancel any existing pre-fetch for a different mode
        if self._prefetched_mode and self._prefetched_mode != practice_mode:
            self._cancel_prefetch()

        # If we already have pre-fetched content for this mode, do nothing
        if self._prefetched_text is not None and self._prefetched_mode == practice_mode:
            return

        try:
            if practice_mode == "sentences":
                text = await generate_sentence_async(self.profile.config)
                keys = self._sentence_to_physical_keys(text)
                language = None
            elif practice_mode == "code":
                lang_config = self.profile.config_overrides.get(
                    "CODE_LANGUAGES", "python,rust,c,cpp"
                )
                allowed_languages = self._parse_language_config(lang_config)
                if not allowed_languages:
                    allowed_languages = ["python", "rust", "c", "cpp"]
                language = random.choice(allowed_languages)
                text = await code_generator.generate_code_snippet_async(
                    language, self.profile.config
                )
                keys = self._sentence_to_physical_keys(text)
            else:
                # Curriculum mode - synchronous generation (fast, no async needed)
                # We'll still pre-fetch the next lesson text
                # Since curriculum generation is fast, we can generate synchronously
                # but we need to run in thread to avoid blocking the UI
                # For now, skip pre-fetching for curriculum mode
                return

            # Store pre-fetched content
            self._prefetched_text = text
            self._prefetched_keys = keys
            self._prefetched_language = language
            self._prefetched_mode = practice_mode
        except Exception as e:
            # Log error and continue without pre-fetching
            import sys

            sys.stderr.write(f"Pre-fetch error: {e}\n")
            self._cancel_prefetch()

    def _start_prefetching(self) -> None:
        """Start pre-fetching the next chunk in the background."""
        if not self.profile:
            return

        # Cancel any existing pre-fetch
        self._cancel_prefetch()

        # Start new pre-fetch task
        self._prefetch_task = asyncio.create_task(self._prefetch_next_chunk())

    def _sentence_to_physical_keys(self, sentence: str) -> List[PhysicalKey]:
        """Convert a sentence string to list of physical keys.

        Args:
            sentence: The sentence string

        Returns:
            List of physical keys corresponding to each character
        """
        return [self._char_to_physical_key(char) for char in sentence]

    def _build_char_to_physical_map(self) -> Dict[str, PhysicalKey]:
        """Build a mapping from characters to physical keys.

        Returns:
            Dictionary mapping characters to their corresponding physical keys
        """
        char_map: Dict[str, PhysicalKey] = {}
        for key in PhysicalKey:
            # Check unmodified
            char = self.resolver.resolve(key.value)
            if char:
                char_map[char] = key

            # Check shifted
            self.resolver.update_modifiers(shift=True)
            char_shifted = self.resolver.resolve(key.value)
            if char_shifted:
                char_map[char_shifted] = key
            self.resolver.update_modifiers(shift=False)  # Reset
        return char_map

    def _build_key_label_cache(self) -> Dict[PhysicalKey, str]:
        """Build a cache of keyboard key labels for display.

        Returns:
            Dictionary mapping physical keys to their display labels
        """
        label_cache: Dict[PhysicalKey, str] = {}
        for key in PhysicalKey:
            if key in DISPLAY_MAP:
                label = DISPLAY_MAP[key]
            else:
                # Resolve via XKB
                label = self.resolver.resolve(key.value) or ""
                # If label is a control char (like \x1b), fallback to name
                if label and (ord(label[0]) < 32):
                    label = key.name.replace("KEY_", "")

            # Upper case for consistency
            if len(label) == 1:
                label = label.upper()

            label_cache[key] = label
        return label_cache

    def _char_to_physical_key(self, char: str) -> PhysicalKey:
        """Convert a single character to its corresponding physical key.

        Args:
            char: The character to convert

        Returns:
            Physical key corresponding to the character
        """
        # Handle special characters
        if char == " ":
            return PhysicalKey.KEY_SPACE
        elif char == "\n":
            return PhysicalKey.KEY_ENTER
        elif char == "\t":
            return PhysicalKey.KEY_TAB
        elif char == "\r":
            # Carriage return, treat as Enter
            return PhysicalKey.KEY_ENTER

        # Look up in character map
        physical_key = self.char_to_physical.get(char)
        if physical_key:
            return physical_key

        # Fallback: try to find a key that produces this char with shift
        # For simplicity, use space as fallback
        return PhysicalKey.KEY_SPACE

    def _parse_language_config(self, config_str: str) -> List[str]:
        """Parse comma-separated language configuration.

        Args:
            config_str: Comma-separated string like "python,rust,c"

        Returns:
            List of valid language strings, stripped and lowercased
        """
        if not config_str:
            return []

        languages = []
        for lang in config_str.split(","):
            lang = lang.strip().lower()
            if lang:
                languages.append(lang)

        # Filter to only supported languages
        supported = {"python", "rust", "c", "cpp"}
        return [lang for lang in languages if lang in supported]

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

        self.target_text = self._get_practice_text()

        self.typed_text = ""
        self.refresh_display()

    def repeat_lesson(self) -> None:
        """Repeat the current lesson without progressing.

        If the last drill passed and advanced to next lesson, decrement lesson index
        to stay on the same lesson.
        """
        if (
            self.profile
            and self.profile.current_lesson_index > self.previous_lesson_index
        ):
            # Decrement index to stay on the same lesson
            self.profile.current_lesson_index = self.previous_lesson_index
        self.start_new_session()

    def load_next_chunk(self) -> None:
        """Load the next chunk of text within the same session.

        Updates cumulative statistics and generates new practice text
        when the current chunk is completed.
        """
        self.cumulative_typed_chars += len(self.typed_text)
        self.cumulative_errors += self.current_chunk_errors
        self.chunks_completed += 1

        self.target_text = self._get_practice_text()

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
        wpm, acc = self._calculate_final_statistics()

        # Determine if drill passed based on practice mode
        passed = self._evaluate_drill_performance(wpm, acc)

        # Update user progress and records
        self._update_user_progress(wpm, passed)

        # Show statistics screen or auto-advance
        self._show_drill_results(wpm, acc, passed)

    def _calculate_final_statistics(self) -> Tuple[int, int]:
        """Calculate final WPM and accuracy for completed drill.

        Returns:
            Tuple of (WPM, accuracy_percentage)
        """
        elapsed = self._get_config("DRILL_DURATION") / 60  # Normalized to full duration
        wpm = round((self.cumulative_typed_chars / 5) / elapsed)
        total_ops = self.cumulative_typed_chars + self.cumulative_errors
        acc = round(
            ((self.cumulative_typed_chars - self.cumulative_errors) / max(1, total_ops))
            * 100
        )
        return wpm, acc

    def _evaluate_drill_performance(self, wpm: int, acc: int) -> bool:
        """Evaluate if drill passed based on practice mode and requirements.

        Args:
            wpm: Words per minute achieved
            acc: Accuracy percentage achieved

        Returns:
            True if drill passed, False otherwise
        """
        if not self.profile:
            return False

        practice_mode = self.profile.config_overrides.get("PRACTICE_MODE", "curriculum")

        if practice_mode == "curriculum":
            # Curriculum mode: evaluate lesson requirements
            self.previous_lesson_index = self.profile.current_lesson_index
            lesson = LESSONS[self.profile.current_lesson_index]
            passed = acc >= lesson["target_acc"] and wpm >= lesson["target_wpm"]
            self.last_drill_passed = passed

            if passed:
                self.notify(f"LEVEL UP: {lesson['name']} Cleared!")
            else:
                self.notify(
                    "Requirements not met. Lesson will repeat.", severity="warning"
                )
            return passed
        else:
            # Sentence or code practice mode: always "passed" for UI purposes
            mode_name = "Sentence" if practice_mode == "sentences" else "Code"
            self.notify(f"{mode_name} practice completed!")
            self.last_drill_passed = True
            return True

    def _update_user_progress(self, wpm: int, passed: bool) -> None:
        """Update user profile with drill results and progress.

        Args:
            wpm: Words per minute achieved
            passed: Whether the drill passed
        """
        if not self.profile:
            return

        if (
            passed
            and self.profile.config_overrides.get("PRACTICE_MODE", "curriculum")
            == "curriculum"
        ):
            # Advance to next lesson in curriculum mode
            self.profile.current_lesson_index += 1
            if self.profile.current_lesson_index >= len(LESSONS):
                self.profile.current_lesson_index = len(LESSONS) - 1

        # Update records
        if wpm > self.profile.wpm_record:
            self.profile.wpm_record = wpm
        self.profile.total_drills += 1
        self.profile.save()

    def _show_drill_results(self, wpm: int, acc: int, passed: bool) -> None:
        """Show drill results via stats screen or auto-advance.

        Args:
            wpm: Words per minute achieved
            acc: Accuracy percentage achieved
            passed: Whether the drill passed
        """
        if self.show_stats_pref:
            self.push_screen(
                StatsScreen(wpm, acc, self.cumulative_errors, passed),
                lambda result: self.repeat_lesson()
                if result == "repeat"
                else self.start_new_session(),
            )
        else:
            if passed:
                action_text = (
                    "[reverse] PRESS ENTER TO START NEXT SESSION [/]\n"
                    "[reverse] PRESS R TO REPEAT LESSON [/]"
                )
            else:
                action_text = "[reverse] PRESS ENTER TO REPEAT LESSON [/]"
            self.query_one("#typing-area").update(
                f"\n[#9ece6a]SESSION COMPLETE[/]\n\n"
                f"WPM: {wpm} | ACC: {acc}% | ERRORS: {self.cumulative_errors}\n\n"
                f"{action_text}"
            )

    def apply_profile_config(self) -> None:
        """Apply the configuration saved in the user's profile.

        Updates UI visibility and preferences based on profile overrides.
        """
        config = self.profile.config
        self.show_stats_pref = config["SHOW_STATS_ON_END"]

        # Update UI visibility
        self.query_one("#keyboard-section").set_class(
            not config["SHOW_QWERTY"], "hidden"
        )
        self.query_one("#finger-guide-wrapper").set_class(
            not config["SHOW_FINGERS"], "hidden"
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
        lesson = LESSONS[self.profile.current_lesson_index]
        algo_type = lesson.get("algo")

        # Handle sentence algorithm specially
        if algo_type == "sentence":
            return self._generate_sentence_text()

        row_key = lesson.get("row", "home")
        row_data = LAYOUT.get(row_key)

        # Generate physical keys using appropriate algorithm
        physical_keys = self._generate_physical_keys(algo_type, row_data)
        self.target_keys = physical_keys

        # Convert physical keys to characters
        shift_mode = lesson.get("shift_mode", "off")
        return self._render_keys_to_text(physical_keys, shift_mode)

    def _generate_sentence_text(self) -> str:
        """Generate sentence practice text.

        Returns:
            Sentence string for practice
        """
        sentence = generate_sentence(self.profile.config)
        self.target_keys = self._sentence_to_physical_keys(sentence)
        return sentence

    def _generate_physical_keys(
        self, algo_type: str, row_data: Dict
    ) -> List[PhysicalKey]:
        """Generate physical keys using the specified algorithm.

        Args:
            algo_type: Algorithm type (repeat, adjacent, alternating, etc.)
            row_data: Keyboard row layout data

        Returns:
            List of physical keys for practice
        """
        should_shuffle = self.chunks_completed >= self._get_config("SHUFFLE_AFTER")

        # Algorithm strategy pattern
        algorithms = {
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

        generator = algorithms.get(algo_type)
        if generator:
            return generator()
        else:
            # Default: random keys
            all_keys = row_data["left"] + row_data["right"]
            return [random.choice(all_keys) for _ in range(40)]

    def _render_keys_to_text(
        self, physical_keys: List[PhysicalKey], shift_mode: str
    ) -> str:
        """Convert physical keys to text characters.

        Args:
            physical_keys: List of physical keys
            shift_mode: Shift mode ("off", "always", "mixed")

        Returns:
            Text string for typing practice
        """
        rendered = []
        for key in physical_keys:
            if key == PhysicalKey.KEY_SPACE:
                rendered.append(" ")
                continue

            use_shift = self._should_use_shift(shift_mode)
            char = self._resolve_key_character(key, use_shift)
            rendered.append(char or "")

        return "".join(rendered)

    def _should_use_shift(self, shift_mode: str) -> bool:
        """Determine if shift should be used for the current key.

        Args:
            shift_mode: Shift mode ("off", "always", "mixed")

        Returns:
            True if shift should be used, False otherwise
        """
        if shift_mode == "always":
            return True
        elif shift_mode == "mixed":
            return random.choice([True, False])
        else:
            return False

    def _resolve_key_character(
        self, key: PhysicalKey, use_shift: bool
    ) -> Optional[str]:
        """Resolve a physical key to its character representation.

        Args:
            key: Physical key to resolve
            use_shift: Whether to use shift modifier

        Returns:
            Character representation or None
        """
        self.resolver.update_modifiers(shift=use_shift)
        char = self.resolver.resolve(key.value)

        # Fallback if shift produced nothing (unlikely for standard keys)
        if not char and use_shift:
            self.resolver.update_modifiers(shift=False)
            char = self.resolver.resolve(key.value)

        return char


if __name__ == "__main__":
    TypingTutor().run()
