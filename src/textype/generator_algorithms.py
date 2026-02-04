"""Text generation algorithms for typing practice patterns.

This module contains algorithms that generate sequences of physical keys
for different typing practice patterns (isolation, adjacency, alternating,
mirroring, rolls, and pseudo-words).
"""
import asyncio
import random
import subprocess
from pathlib import Path
from typing import List
from keyboard import PhysicalKey, RowLayout
from text_normalizer import normalize_text

# Optional dependencies
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


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


def generate_sentence() -> str:
    """Generate a random practice sentence.

    Returns a random sentence from the configured sentence list.
    This is used for sentence practice mode.
    """
    import config

    source = config.SENTENCE_SOURCE

    # 1. External API (Online)
    if source == "api" and HAS_REQUESTS:
        try:
            response = requests.get(config.QUOTE_API_URL, timeout=2)
            if response.status_code == 200:
                # Adjust parsing based on specific API schema
                data = response.json()
                text = data.get("text", "")
                author = data.get("author")
                if author:
                    return normalize_text(f"{text}\n{author}")
                return normalize_text(text)
        except Exception:
            pass

    if source == "cmd" and config.CODE_COMMAND:
        try:
            result = subprocess.check_output(config.CODE_COMMAND, shell=True, timeout=2)
            return normalize_text(result.decode().strip())
        except Exception:
            pass

    if source == "ai" and HAS_REQUESTS:
        try:
            payload = {
                "model": "codellama",
                "prompt": "Provide sentences for typing practice.",
                "stream": False,
            }
            response = requests.post(config.AI_ENDPOINT, json=payload, timeout=5)
            if response.status_code == 200:
                return normalize_text(response.json().get("response", "").strip())
        except Exception:
            pass

    if source == "file" or (source == "api" and config.SENTENCES_FILE):
        if Path(config.SENTENCES_FILE).exists():
            with open(config.SENTENCES_FILE, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    return normalize_text(random.choice(lines))

    # 3. Fallback: Static list in config.py
    return normalize_text(random.choice(config.SENTENCES))


async def generate_sentence_async() -> str:
    """Generate a random practice sentence asynchronously.

    Returns a random sentence from the configured sentence list.
    This is used for sentence practice mode with async pre-fetching.
    """
    # Run the synchronous function in a thread to avoid blocking
    return await asyncio.to_thread(generate_sentence)


if __name__ == "__main__":
    from keyboard import LAYOUT

    row_keys = LAYOUT["home"]
    print(single_key_repeat(row_keys["left"], reps=3))
    print(same_hand_adjacent(row_keys))
    print(alternating_pairs(row_keys))
    print(mirror_pairs(row_keys))
    print(rolls(row_keys))
    print(pseudo_words(row_keys))
    print(generate_sentence())
