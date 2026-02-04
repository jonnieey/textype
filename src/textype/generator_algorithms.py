"""Text generation algorithms for typing practice patterns.

This module contains algorithms that generate sequences of physical keys
for different typing practice patterns (isolation, adjacency, alternating,
mirroring, rolls, and pseudo-words).
"""
import random
from typing import List
from textype.keyboard import PhysicalKey, RowLayout


def single_key_repeat(
    keys: List[PhysicalKey], reps: int = 4, shuffle: bool = True
) -> List[PhysicalKey]:
    """Generate sequence for single key repetition practice.

    Builds muscle memory through isolation by repeating each key multiple
    times before moving to the next key.

    Args:
        keys: List of physical keys to practice
        reps: Number of repetitions per key (default: 4)
        shuffle: Whether to shuffle the order of keys (default: True)

    Returns:
        List of physical keys with spaces between repetitions

    Example:
        >>> from keyboard import LAYOUT
        >>> keys = LAYOUT["home"]["left"]
        >>> seq = single_key_repeat(keys, reps=2, shuffle=False)
        >>> len(seq)
        11  # 4 keys * 2 reps + 3 spaces (last space removed)
    """
    pool = keys[:]
    if shuffle:
        random.shuffle(pool)

    seq = []
    for key in pool:
        seq.extend([key] * reps)
        seq.append(PhysicalKey.KEY_SPACE)
    return seq[:-1] if seq else []


def same_hand_adjacent(
    row_keys: RowLayout, reps: int = 3, shuffle: bool = True
) -> List[PhysicalKey]:
    """Generate sequence for same-hand adjacent key practice.

    Teaches finger neighbors by creating pairs of adjacent keys on
    the same hand.

    Args:
        row_keys: Dictionary with 'left' and 'right' key lists
        reps: Number of repetitions for each pair (default: 3)
        shuffle: Whether to shuffle the order of pairs (default: True)

    Returns:
        List of physical keys with spaces between pairs

    Example:
        >>> from keyboard import LAYOUT
        >>> seq = same_hand_adjacent(LAYOUT["home"], reps=1, shuffle=False)
        >>> # Creates pairs: (A,S), (S,D), (D,F), (J,K), (K,L), (L,;)
    """
    pairs = []
    for hand_keys in [row_keys["left"], row_keys["right"]]:
        for idx in range(len(hand_keys) - 1):
            # Creates pairs like [ (A,S), (S,D), ... ]
            pairs.append([hand_keys[idx], hand_keys[idx + 1]])

    pool = pairs * reps
    if shuffle:
        random.shuffle(pool)

    # Flatten the list of lists with spaces
    seq = []
    for pair in pool:
        seq.extend(pair)
        seq.append(PhysicalKey.KEY_SPACE)
    return seq[:-1] if seq else []


def alternating_pairs(
    row_keys: RowLayout, reps: int = 4, shuffle: bool = True
) -> List[PhysicalKey]:
    """Generate sequence for alternating hand practice.

    Teaches rhythm and balance by creating pairs of keys that alternate
    between left and right hands.

    Args:
        row_keys: Dictionary with 'left' and 'right' key lists
        reps: Number of repetitions for each pair (default: 4)
        shuffle: Whether to shuffle the order of pairs (default: True)

    Returns:
        List of physical keys with spaces between pairs

    Example:
        >>> from keyboard import LAYOUT
        >>> seq = alternating_pairs(LAYOUT["home"], reps=1, shuffle=False)
        >>> # Creates pairs: (A,J), (S,K), (D,L), (F,;)
    """
    pairs = []
    for left_key, right_key in zip(row_keys["left"], row_keys["right"]):
        pairs.append([left_key, right_key])

    pool = pairs * reps
    if shuffle:
        random.shuffle(pool)

    seq = []
    for pair in pool:
        seq.extend(pair)
        seq.append(PhysicalKey.KEY_SPACE)
    return seq[:-1] if seq else []


def mirror_pairs(
    row_keys: RowLayout, reps: int = 4, shuffle: bool = True
) -> List[PhysicalKey]:
    """Generate sequence for mirror finger practice.

    Associates corresponding fingers on opposite hands by creating
    mirror pairs (e.g., left index with right index).

    Args:
        row_keys: Dictionary with 'left' and 'right' key lists
        reps: Number of repetitions for each pair (default: 4)
        shuffle: Whether to shuffle the order of pairs (default: True)

    Returns:
        List of physical keys with spaces between pairs

    Example:
        >>> from keyboard import LAYOUT
        >>> seq = mirror_pairs(LAYOUT["home"], reps=1, shuffle=False)
        >>> # Creates pairs: (A,;), (S,L), (D,K), (F,J)
    """
    pairs = []
    for idx in range(len(row_keys["left"])):
        pairs.append([row_keys["left"][idx], row_keys["right"][-(idx + 1)]])

    pool = pairs * reps
    if shuffle:
        random.shuffle(pool)

    seq = []
    for pair in pool:
        seq.extend(pair)
        seq.append(PhysicalKey.KEY_SPACE)
    return seq[:-1] if seq else []


def rolls(
    row_keys: RowLayout, reps: int = 2, shuffle: bool = True
) -> List[PhysicalKey]:
    """Generate sequence for finger roll practice.

    Teaches inward and outward finger flows by creating sequences
    that roll across fingers in natural patterns.

    Args:
        row_keys: Dictionary with 'left' and 'right' key lists
        reps: Number of repetitions for each pattern (default: 2)
        shuffle: Whether to shuffle the order of patterns (default: True)

    Returns:
        List of physical keys with spaces between patterns

    Example:
        >>> from keyboard import LAYOUT
        >>> seq = rolls(LAYOUT["home"], reps=1, shuffle=False)
        >>> # Creates patterns: A,S,D,F (inward), F,D,S,A (outward),
        >>> # J,K,L,; (inward), ;,L,K,J (outward)
    """
    left_keys, right_keys = row_keys["left"], row_keys["right"]
    patterns = [
        left_keys,  # Inward (e.g. A,S,D,F)
        left_keys[::-1],  # Outward (e.g. F,D,S,A)
        right_keys,
        right_keys[::-1],
    ]

    pool = patterns * reps
    if shuffle:
        random.shuffle(pool)

    seq = []
    for pattern in pool:
        seq.extend(pattern)
        seq.append(PhysicalKey.KEY_SPACE)
    return seq[:-1] if seq else []


def pseudo_words(row_keys: RowLayout, count: int = 10) -> List[PhysicalKey]:
    """Generate sequence for pseudo-word practice.

    Synthesizes realistic but fake word patterns from the practice keys
    to simulate actual typing scenarios.

    Args:
        row_keys: Dictionary with 'left' and 'right' key lists
        count: Number of pseudo-words to generate (default: 10)

    Returns:
        List of physical keys forming pseudo-words with spaces

    Example:
        >>> from keyboard import LAYOUT
        >>> seq = pseudo_words(LAYOUT["home"], count=2)
        >>> # Might generate: "asdf jkl;" or "sadf lkj;"
    """
    all_keys = row_keys["left"] + row_keys["right"]
    seq = []
    for _ in range(count):
        length = random.choice([3, 4, 5])
        # Add a word
        seq.extend(random.choices(all_keys, k=length))
        # Add a space
        seq.append(PhysicalKey.KEY_SPACE)

    return seq


if __name__ == "__main__":
    from textype.keyboard import LAYOUT

    row_keys = LAYOUT["home"]
    print(single_key_repeat(row_keys["left"], reps=3))
    print(same_hand_adjacent(row_keys))
    print(alternating_pairs(row_keys))
    print(mirror_pairs(row_keys))
    print(rolls(row_keys))
    print(pseudo_words(row_keys))
