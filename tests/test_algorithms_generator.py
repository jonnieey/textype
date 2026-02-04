"""Unit tests for the algorithms_generator module."""

import pytest
from textype.keyboard import PhysicalKey, LAYOUT
from textype.algorithms_generator import (
    single_key_repeat,
    same_hand_adjacent,
    alternating_pairs,
    mirror_pairs,
    rolls,
    pseudo_words,
)


@pytest.fixture
def home_row_keys():
    """Provides the home row keys for testing."""
    return LAYOUT["home"]


class TestAlgorithmsGenerator:
    """Tests the key sequence generation algorithms."""

    def test_single_key_repeat(self):
        """Tests the single_key_repeat algorithm."""
        keys = [PhysicalKey.KEY_A, PhysicalKey.KEY_S]
        result = single_key_repeat(keys, reps=2, shuffle=False)
        expected = [
            PhysicalKey.KEY_A,
            PhysicalKey.KEY_A,
            PhysicalKey.KEY_SPACE,
            PhysicalKey.KEY_S,
            PhysicalKey.KEY_S,
        ]
        assert result == expected

    def test_single_key_repeat_empty(self):
        """Tests single_key_repeat with an empty list of keys."""
        assert single_key_repeat([], reps=2) == []

    def test_same_hand_adjacent(self, home_row_keys):
        """Tests the same_hand_adjacent algorithm."""
        result = same_hand_adjacent(home_row_keys, reps=1, shuffle=False)
        # 3 left hand pairs, 3 right hand pairs, 5 spaces
        assert len(result) == (3 * 2) + (3 * 2) + 5
        assert PhysicalKey.KEY_A in result
        assert PhysicalKey.KEY_S in result

    def test_same_hand_adjacent_empty(self):
        """Tests same_hand_adjacent with empty row keys."""
        assert same_hand_adjacent({"left": [], "right": []}) == []

    def test_alternating_pairs(self, home_row_keys):
        """Tests the alternating_pairs algorithm."""
        result = alternating_pairs(home_row_keys, reps=1, shuffle=False)
        # 4 pairs, 3 spaces
        assert len(result) == 4 * 2 + 3
        assert result[0:2] == [PhysicalKey.KEY_A, PhysicalKey.KEY_J]

    def test_alternating_pairs_empty(self):
        """Tests alternating_pairs with empty row keys."""
        assert alternating_pairs({"left": [], "right": []}) == []

    def test_mirror_pairs(self, home_row_keys):
        """Tests the mirror_pairs algorithm."""
        result = mirror_pairs(home_row_keys, reps=1, shuffle=False)
        assert len(result) == 4 * 2 + 3
        assert result[0:2] == [PhysicalKey.KEY_A, PhysicalKey.KEY_SEMICOLON]

    def test_mirror_pairs_empty(self):
        """Tests mirror_pairs with empty row keys."""
        assert mirror_pairs({"left": [], "right": []}) == []

    def test_rolls(self, home_row_keys):
        """Tests the rolls algorithm."""
        result = rolls(home_row_keys, reps=1, shuffle=False)
        # 4 patterns of 4 keys, 3 spaces
        assert len(result) == 4 * 4 + 3
        assert result[0:4] == [
            PhysicalKey.KEY_A,
            PhysicalKey.KEY_S,
            PhysicalKey.KEY_D,
            PhysicalKey.KEY_F,
        ]

    def test_rolls_empty(self):
        """Tests rolls with empty row keys."""
        assert rolls({"left": [], "right": []}) == []

    def test_pseudo_words(self, home_row_keys):
        """Tests the pseudo_words algorithm."""
        result = pseudo_words(home_row_keys, count=5)
        # 5 words + 5 spaces
        assert len(result) >= 5 * (3 + 1)  # Min word length is 3
        assert PhysicalKey.KEY_SPACE in result

    def test_pseudo_words_empty(self):
        """Tests pseudo_words with empty row keys."""
        assert pseudo_words({"left": [], "right": []}, count=5) == []
