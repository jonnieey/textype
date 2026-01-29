from collections import namedtuple

SHOW_QWERTY = False
SHOW_FINGERS = False
HARD_MODE = True
SHOW_STATS_ON_END = False

LESSONS = [
    # Stage 1: Home Row Intro
    {
        "name": "Home Row: Basics",
        "keys": "ASDFG HJKL;",
        "type": "repeat",
        "target_acc": 80,
        "target_wpm": 0,
    },
    {
        "name": "Home Row: Combinations",
        "keys": "ASDFG HJKL;",
        "type": "scramble",
        "target_acc": 80,
        "target_wpm": 0,
    },
    {
        "name": "Home Row: Speed Test",
        "keys": "ASDFG HJKL;",
        "type": "scramble",
        "target_acc": 0,
        "target_wpm": 7,
    },
    # Stage 2: Top Row Intro
    {
        "name": "Top Row: Basics",
        "keys": "QWERT YUIOP",
        "type": "repeat",
        "target_acc": 80,
        "target_wpm": 0,
    },
    {
        "name": "Top Row: Combinations",
        "keys": "QWERT YUIOP",
        "type": "scramble",
        "target_acc": 80,
        "target_wpm": 0,
    },
    {
        "name": "Top Row: Speed Test",
        "keys": "QWERT YUIOP",
        "type": "scramble",
        "target_acc": 0,
        "target_wpm": 7,
    },
]

SENTENCES = [
    "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
    "PRACTICE UNTIL THE MOTIONS BECOME SECOND NATURE",
    "RELIANCE ON SIGHT IS THE ENEMY OF SPEED",
    "FLUIDITY MATTERS MORE THAN RAW VELOCITY",
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
