"""Utility script to map evdev scancodes to characters using XKB.

This script scans through evdev scancodes 1-128 and prints their
character mappings with and without shift modifier. Useful for
debugging keyboard layout issues.
"""
from xkb_resolver import XKBResolver


def main() -> None:
    """Print evdev scancode to character mapping."""
    resolver = XKBResolver()

    print(f"{'Code':<6} | {'Char':<6} | {'Shifted':<8}")
    print("-" * 26)

    # Standard evdev range 1-128 covers almost all standard keyboard keys
    for code in range(1, 128):
        # Reset modifiers
        resolver.update_modifiers(shift=False)
        char = resolver.resolve(code)

        # Check shifted version
        resolver.update_modifiers(shift=True)
        char_shifted = resolver.resolve(code)

        # Only print if it resolves to something printable/visible
        if char or char_shifted:
            # Handle non-printable or None
            c_disp = repr(char) if char else "None"
            s_disp = repr(char_shifted) if char_shifted else "None"

            print(f"{code:<6} | {c_disp:<6} | {s_disp:<8}")


if __name__ == "__main__":
    main()
