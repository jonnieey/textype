"""XKB keycode to character resolver for keyboard layout mapping.

This module provides functionality to map physical key scancodes to
characters based on the current keyboard layout using the XKB library.
"""
import xkbcommon.xkb as xkb
from typing import Optional


class XKBResolver:
    """Resolves physical key scancodes to characters using XKB.

    This class uses the XKB library to map evdev scancodes to characters
    based on the current keyboard layout and modifier state (shift, altgr).

    Attributes:
        ctx: XKB context for keymap creation
        keymap: XKB keymap representing the current keyboard layout
        state: XKB state tracking modifier keys
    """

    def __init__(self) -> None:
        """Initialize the XKB resolver with current system layout.

        Creates a new XKB context and loads the keymap from system
        defaults (respecting XKB_DEFAULT_LAYOUT environment variable).

        Example:
            >>> resolver = XKBResolver()
            >>> # Ready to resolve keys based on current layout
        """
        self.ctx = xkb.Context()
        self.keymap = self.ctx.keymap_new_from_names()
        self.state = self.keymap.state_new()

    def update_modifiers(self, shift: bool = False, altgr: bool = False) -> None:
        """Update the modifier state for character resolution.

        Args:
            shift: Whether shift key is pressed (default: False)
            altgr: Whether AltGr key is pressed (default: False)

        Example:
            >>> resolver = XKBResolver()
            >>> resolver.update_modifiers(shift=True)
            >>> # Now resolve() will return shifted characters
        """
        mods = 0

        def mod(name: str) -> int:
            """Get modifier index by name."""
            return self.keymap.mod_get_index(name)

        if shift:
            mods |= 1 << mod("Shift")
        if altgr:
            mods |= 1 << mod("ISO_Level3_Shift")

        self.state.update_mask(mods, 0, 0, 0, 0, 0)

    def resolve(self, evdev_code: int) -> Optional[str]:
        """Resolve an evdev scancode to a character.

        Args:
            evdev_code: Evdev scancode (PhysicalKey.value)

        Returns:
            Character string if resolvable, None otherwise

        Example:
            >>> resolver = XKBResolver()
            >>> # Assuming US QWERTY layout
            >>> resolver.resolve(30)  # KEY_A scancode
            'a'
            >>> resolver.update_modifiers(shift=True)
            >>> resolver.resolve(30)
            'A'

        Note:
            Evdev scancodes need +8 offset to convert to XKB keycodes.
        """
        xkb_code = evdev_code + 8  # IMPORTANT: evdev to XKB offset
        sym = self.state.key_get_one_sym(xkb_code)
        if sym == xkb.lib.XKB_KEY_NoSymbol:
            return None
        return xkb.keysym_to_string(sym)
