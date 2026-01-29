from collections import namedtuple

SHOW_QWERTY = False
SHOW_FINGERS = False
HARD_MODE = True
SHOW_STATS_ON_END = False
DRILL_DURATION = 300  # Seconds (5 minutes)

LESSONS = [
    {
        "name": "1.1: Isolation",
        "algo": "repeat",
        "row": "home",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "1.2: Adjacency",
        "algo": "adjacent",
        "row": "home",
        "target_acc": 95,
        "target_wpm": 15,
    },
    {
        "name": "1.3: Alternating",
        "algo": "alternating",
        "row": "home",
        "target_acc": 92,
        "target_wpm": 20,
    },
    {
        "name": "1.4: Mirroring",
        "algo": "mirror",
        "row": "home",
        "target_acc": 92,
        "target_wpm": 20,
    },
    {
        "name": "1.5: Rolling",
        "algo": "rolls",
        "row": "home",
        "target_acc": 90,
        "target_wpm": 25,
    },
    {
        "name": "1.6: Synthesis",
        "algo": "pseudo",
        "row": "home",
        "target_acc": 95,
        "target_wpm": 30,
    },
]

SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "Practice until the motions become second nature",
    "Reliance on sight is the enemy of speed",
    "Fluidity matters more than raw velocity",
]

ID_MAP = {
    " ": "space",
    ";": "semicolon",
    ",": "comma",
    ".": "dot",
    "/": "slash",
    "'": "quote",
    "[": "left-bracket",
    "]": "right-bracket",
    "-": "minus",
    "=": "equals",
}

FingerDimensions = namedtuple("FingerDimensions", ["height", "width"])

FINGER_HEIGHTS = {
    "L1": FingerDimensions(4, 7),
    "L2": FingerDimensions(6, 7),
    "L3": FingerDimensions(7, 7),
    "L4": FingerDimensions(6, 7),
    "THUMB": FingerDimensions(2, 20),
    "R1": FingerDimensions(6, 7),
    "R2": FingerDimensions(7, 7),
    "R3": FingerDimensions(6, 7),
    "R4": FingerDimensions(4, 7),
}

MAX_FINGER_HEIGHT = max(dimensions.height for dimensions in FINGER_HEIGHTS.values())

FINGER_MAP = {
    # Top Row
    "Q": "L1",
    "W": "L2",
    "E": "L3",
    "R": "L4",
    "T": "L4",
    "Y": "R1",
    "U": "R1",
    "I": "R2",
    "O": "R3",
    "P": "R4",
    "[": "R4",
    "]": "R4",
    # Home Row
    "A": "L1",
    "S": "L2",
    "D": "L3",
    "F": "L4",
    "G": "L4",
    "H": "R1",
    "J": "R1",
    "K": "R2",
    "L": "R3",
    ";": "R4",
    "'": "R4",
    # Bottom Row
    "Z": "L1",
    "X": "L2",
    "C": "L3",
    "V": "L4",
    "B": "L4",
    "N": "R1",
    "M": "R1",
    ",": "R2",
    ".": "R3",
    "/": "R4",
    " ": "THUMB",
}
