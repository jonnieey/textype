import random

# Hand definitions based on standard QWERTY
LAYOUT = {
    "home": {"left": "asdf", "right": "jkl;"},
    "top": {"left": "qwer", "right": "uiop"},
    "bottom": {"left": "zxcv", "right": "nm,."},
    "numbers": {"left": "12345", "right": "67890"},
}


def single_key_repeat(keys, reps=4, shuffle=True):
    """Algorithm 1: Build muscle memory through isolation."""
    # Convert string to list to shuffle
    key_list = list(keys)
    if shuffle:
        random.shuffle(key_list)
    return " ".join(["".join([key] * reps) for key in key_list])


def same_hand_adjacent(row_keys, reps=3, shuffle=True):
    """Algorithm 2: Learn finger neighbors."""
    pairs = []
    for hand_keys in [row_keys["left"], row_keys["right"]]:
        for idx in range(len(hand_keys) - 1):
            pairs.append(hand_keys[idx] + hand_keys[idx + 1])

    # Create the full list of items and shuffle
    items = pairs * reps
    if shuffle:
        random.shuffle(items)
    return " ".join(items)


def alternating_pairs(row_keys, reps=4, shuffle=True):
    """Algorithm 3: Rhythm & Balance training."""
    pairs = [
        left_key + right_key
        for left_key, right_key in zip(row_keys["left"], row_keys["right"])
    ]
    items = pairs * reps
    if shuffle:
        random.shuffle(items)
    return " ".join(items)


def mirror_pairs(row_keys, reps=4, shuffle=True):
    """Algorithm 4: Associate corresponding fingers on opposite hands."""
    # A with ;, S with L, etc.
    pairs = [
        row_keys["left"][idx] + row_keys["right"][-(idx + 1)]
        for idx in range(len(row_keys["left"]))
    ]
    items = pairs * reps
    if shuffle:
        random.shuffle(items)
    return " ".join(items)


def rolls(row_keys, reps=2, shuffle=True):
    """Algorithm 6: Inward and Outward finger flows."""
    left_keys, right_keys = row_keys["left"], row_keys["right"]
    # Inward: ASDF -> ASDF, Outward: ASDF -> FDSA
    # Create the 4 distinct roll patterns
    patterns = [
        left_keys,  # Left Inward (e.g. asdf)
        left_keys[::-1],  # Left Outward (e.g. fdsa)
        right_keys,  # Right Inward
        right_keys[::-1],  # Right Outward
    ]

    # Create the full list of items to display
    items = patterns * reps
    if shuffle:
        random.shuffle(items)
    return " ".join(items)


def pseudo_words(row_keys, count=10):
    """Algorithm 12: Synthesis into realistic but fake word patterns."""
    all_keys = row_keys["left"] + row_keys["right"]
    words = []
    for _ in range(count):
        length = random.choice([3, 4, 5])
        words.append("".join(random.choices(all_keys, k=length)))
    return " ".join(words)


if __name__ == "__main__":
    # for row_name, row_keys in LAYOUT.items():
    row_keys = LAYOUT["home"]
    print(single_key_repeat(row_keys["left"], reps=3))
    print(single_key_repeat(row_keys["right"], reps=3))
    # print(same_hand_adjacent(row_keys))
    # print(alternating_pairs(row_keys))
    # print(mirror_pairs(row_keys))
    # print(rolls(row_keys))
    # print(pseudo_words(row_keys))
