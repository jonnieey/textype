"""Unit tests for the xkb_resolver module."""

from unittest.mock import patch, MagicMock

import pytest
from textype.xkb_resolver import XKBResolver


@pytest.fixture
def mock_xkb():
    """Mocks the xkbcommon library for testing."""
    with patch("textype.xkb_resolver.xkb") as mock:
        yield mock


class TestXKBResolver:
    """Tests the XKBResolver class for keycode-to-character mapping."""

    def test_init(self, mock_xkb):
        """Tests that the XKBResolver initializes correctly."""
        mock_context = MagicMock()
        mock_keymap = MagicMock()
        mock_state = MagicMock()

        mock_xkb.Context.return_value = mock_context
        mock_context.keymap_new_from_names.return_value = mock_keymap
        mock_keymap.state_new.return_value = mock_state

        resolver = XKBResolver()

        mock_xkb.Context.assert_called_once()
        mock_context.keymap_new_from_names.assert_called_once()
        mock_keymap.state_new.assert_called_once()
        assert resolver.ctx == mock_context
        assert resolver.keymap == mock_keymap
        assert resolver.state == mock_state

    def test_resolve_simple_key(self, mock_xkb):
        """Tests resolving a simple key without modifiers."""
        resolver = XKBResolver()

        # Mock the key_get_one_sym and keysym_to_string methods
        resolver.state.key_get_one_sym.return_value = 1
        mock_xkb.keysym_to_string.return_value = "a"

        result = resolver.resolve(30)  # KEY_A scancode

        assert result == "a"
        resolver.state.key_get_one_sym.assert_called_once_with(38)  # 30 + 8

    def test_resolve_shifted_key(self, mock_xkb):
        """Tests resolving a key with the Shift modifier."""
        resolver = XKBResolver()

        resolver.keymap.mod_get_index.return_value = 1  # Mock "Shift" index
        resolver.state.key_get_one_sym.return_value = 2
        mock_xkb.keysym_to_string.return_value = "A"

        resolver.update_modifiers(shift=True)
        result = resolver.resolve(30)

        assert result == "A"
        resolver.state.update_mask.assert_called()

    def test_resolve_altgr_key(self, mock_xkb):
        """Tests resolving a key with the AltGr modifier."""
        resolver = XKBResolver()

        resolver.keymap.mod_get_index.return_value = 2  # Mock "ISO_Level3_Shift" index
        resolver.state.key_get_one_sym.return_value = 3
        mock_xkb.keysym_to_string.return_value = "á"

        resolver.update_modifiers(altgr=True)
        result = resolver.resolve(30)

        assert result == "á"
        resolver.state.update_mask.assert_called()

    def test_resolve_no_symbol(self, mock_xkb):
        """Tests resolving a key that has no symbol."""
        resolver = XKBResolver()

        # Configure the mock to return NoSymbol
        mock_xkb.lib.XKB_KEY_NoSymbol = 0
        resolver.state.key_get_one_sym.return_value = 0

        result = resolver.resolve(1)  # KEY_ESCAPE scancode

        assert result is None
