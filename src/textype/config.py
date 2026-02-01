from collections import namedtuple

SHOW_QWERTY = False
SHOW_FINGERS = False
HARD_MODE = True
SHOW_STATS_ON_END = False
DRILL_DURATION = 300  # Seconds (5 minutes)
SHUFFLE_AFTER = 5  # Shuffle chunks after X repetitions

rows = ("home", "top", "bottom", "numbers")
LESSONS = []
for idx, row in enumerate(rows, start=1):
    LESSONS.extend(
        [
            {
                "name": f"{idx}.1: Isolation",
                "algo": "repeat",
                "row": row,
                "target_acc": 95,
                "target_wpm": 10,
            },
            {
                "name": f"{idx}.2: Adjacency",
                "algo": "adjacent",
                "row": row,
                "target_acc": 95,
                "target_wpm": 10,
            },
            {
                "name": f"{idx}.3: Alternating",
                "algo": "alternating",
                "row": row,
                "target_acc": 92,
                "target_wpm": 10,
            },
            {
                "name": f"{idx}.4: Mirroring",
                "algo": "mirror",
                "row": row,
                "target_acc": 92,
                "target_wpm": 10,
            },
            {
                "name": f"{idx}.5: Rolling",
                "algo": "rolls",
                "row": row,
                "target_acc": 90,
                "target_wpm": 10,
            },
            {
                "name": f"{idx}.6: Synthesis",
                "algo": "pseudo",
                "row": row,
                "target_acc": 95,
                "target_wpm": 10,
            },
        ]
    )

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
