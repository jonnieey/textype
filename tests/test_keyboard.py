"""Unit tests for the keyboard module."""

from textype.keyboard import PhysicalKey, KEYBOARD_ROWS, FINGER_MAP, LAYOUT, DISPLAY_MAP


class TestKeyboardLayout:
    """Tests the integrity and consistency of keyboard layout data structures."""

    def test_physical_key_enum_uniqueness(self):
        """Tests that all PhysicalKey enum values are unique."""
        values = [key.value for key in PhysicalKey]
        assert len(values) == len(set(values))

    def test_keyboard_rows_structure(self):
        """Ensures KEYBOARD_ROWS is a list of lists containing PhysicalKey enums."""
        assert isinstance(KEYBOARD_ROWS, list)
        for row in KEYBOARD_ROWS:
            assert isinstance(row, list)
            assert all(isinstance(key, PhysicalKey) for key in row)

    def test_all_keys_in_finger_map(self):
        """Verifies that all non-modifier keys in KEYBOARD_ROWS are in FINGER_MAP."""
        all_keys = {key for row in KEYBOARD_ROWS for key in row}
        # Assuming certain keys like ESC might not have a finger mapping
        keys_requiring_finger = {
            k for k in all_keys if k not in {PhysicalKey.KEY_ESCAPE}
        }

        for key in keys_requiring_finger:
            assert key in FINGER_MAP, f"{key.name} is missing from FINGER_MAP"

    def test_finger_map_values(self):
        """Checks that FINGER_MAP values are valid finger identifiers."""
        valid_fingers = {"L1", "L2", "L3", "L4", "R1", "R2", "R3", "R4", "THUMB"}
        for finger in FINGER_MAP.values():
            assert finger in valid_fingers

    def test_layout_structure(self):
        """Ensures LAYOUT has the correct structure."""
        assert isinstance(LAYOUT, dict)
        for row_name, row_layout in LAYOUT.items():
            assert isinstance(row_name, str)
            assert isinstance(row_layout, dict)
            assert "left" in row_layout
            assert "right" in row_layout
            assert isinstance(row_layout["left"], list)
            assert isinstance(row_layout["right"], list)

    def test_layout_keys(self):
        """Verifies that all keys in LAYOUT are PhysicalKey enums."""
        for row_layout in LAYOUT.values():
            for hand in ["left", "right"]:
                assert all(isinstance(key, PhysicalKey) for key in row_layout[hand])

    def test_display_map_keys(self):
        """Checks that all keys in DISPLAY_MAP are PhysicalKey enums."""
        assert all(isinstance(key, PhysicalKey) for key in DISPLAY_MAP.keys())
        assert all(isinstance(value, str) for value in DISPLAY_MAP.values())
