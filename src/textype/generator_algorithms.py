import random
from keyboard import PhysicalKey


LAYOUT = {
    "home": {
        "left": [
            PhysicalKey.KEY_A,
            PhysicalKey.KEY_S,
            PhysicalKey.KEY_D,
            PhysicalKey.KEY_F,
        ],
        "right": [
            PhysicalKey.KEY_J,
            PhysicalKey.KEY_K,
            PhysicalKey.KEY_L,
            PhysicalKey.KEY_SEMICOLON,
        ],
    },
    "top": {
        "left": [
            PhysicalKey.KEY_Q,
            PhysicalKey.KEY_W,
            PhysicalKey.KEY_E,
            PhysicalKey.KEY_R,
        ],
        "right": [
            PhysicalKey.KEY_U,
            PhysicalKey.KEY_I,
            PhysicalKey.KEY_O,
            PhysicalKey.KEY_P,
        ],
    },
    "bottom": {
        "left": [
            PhysicalKey.KEY_Z,
            PhysicalKey.KEY_X,
            PhysicalKey.KEY_C,
            PhysicalKey.KEY_V,
        ],
        "right": [
            PhysicalKey.KEY_N,
            PhysicalKey.KEY_M,
            PhysicalKey.KEY_COMMA,
            PhysicalKey.KEY_DOT,
        ],
    },
    "numbers": {
        "left": [
            PhysicalKey.KEY_1,
            PhysicalKey.KEY_2,
            PhysicalKey.KEY_3,
            PhysicalKey.KEY_4,
            PhysicalKey.KEY_5,
        ],
        "right": [
            PhysicalKey.KEY_6,
            PhysicalKey.KEY_7,
            PhysicalKey.KEY_8,
            PhysicalKey.KEY_9,
            PhysicalKey.KEY_0,
            PhysicalKey.KEY_MINUS,
            PhysicalKey.KEY_EQUAL,
        ],
    },
}


def single_key_repeat(keys: list[PhysicalKey], reps=4, shuffle=True):
    """Algorithm 1: Build muscle memory through isolation."""
    pool = keys[:]
    if shuffle:
        random.shuffle(pool)

    seq = []
    for key in pool:
        seq.extend([key] * reps)
        seq.append(PhysicalKey.KEY_SPACE)
    return seq[:-1] if seq else []


def same_hand_adjacent(row_keys, reps=3, shuffle=True):
    """Algorithm 2: Learn finger neighbors."""
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


def alternating_pairs(row_keys, reps=4, shuffle=True):
    """Algorithm 3: Rhythm & Balance training."""
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


def mirror_pairs(row_keys, reps=4, shuffle=True):
    """Algorithm 4: Associate corresponding fingers on opposite hands."""
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


def rolls(row_keys, reps=2, shuffle=True):
    """Algorithm 6: Inward and Outward finger flows."""
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


def pseudo_words(row_keys, count=10):
    """Algorithm 12: Synthesis into realistic but fake word patterns."""
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
    row_keys = LAYOUT["home"]
    print(single_key_repeat(row_keys["left"], reps=3))
    print(same_hand_adjacent(row_keys))
    print(alternating_pairs(row_keys))
    print(mirror_pairs(row_keys))
    print(rolls(row_keys))
    print(pseudo_words(row_keys))
