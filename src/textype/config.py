"""Configuration module for the Textype typing tutor application.

This module contains all configuration constants, lesson definitions, and
UI settings used throughout the application.
"""
from collections import namedtuple
from typing import Dict, List, Tuple, TypedDict


# ============================================================================
# UI Configuration
# ============================================================================

SHOW_QWERTY: bool = False
"""Whether to show the QWERTY keyboard visualization by default."""

SHOW_FINGERS: bool = False
"""Whether to show the finger guide visualization by default."""

HARD_MODE: bool = True
"""Whether to enable hard mode (errors prevent progress)."""

SHOW_STATS_ON_END: bool = False
"""Whether to show statistics screen automatically after each drill."""

DRILL_DURATION: int = 300
"""Duration of each typing drill in seconds (5 minutes)."""

SHUFFLE_AFTER: int = 5
"""Number of repetitions before shuffling practice patterns."""


# ============================================================================
# Lesson Definitions
# ============================================================================


class LessonDict(TypedDict):
    """Type definition for lesson configuration dictionaries.

    Attributes:
        name: Display name of the lesson
        algo: Algorithm identifier for text generation
        row: Keyboard row to focus on
        target_acc: Minimum accuracy percentage required to pass
        target_wpm: Minimum words per minute required to pass
    """

    name: str
    algo: str
    row: str
    target_acc: int
    target_wpm: int


rows: Tuple[str, ...] = ("home", "top", "bottom", "numbers")
"""Available keyboard rows for lessons."""

LESSONS: List[LessonDict] = []
"""List of all typing lessons with progression logic."""

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


# ============================================================================
# Practice Content
# ============================================================================

SENTENCES: List[str] = [
    "The quick brown fox jumps over the lazy dog",
    "Practice until the motions become second nature",
    "Reliance on sight is the enemy of speed",
    "Fluidity matters more than raw velocity",
]
"""Default practice sentences for non-lesson typing."""


# ============================================================================
# Character Mapping
# ============================================================================

ID_MAP: Dict[str, str] = {
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
"""Mapping from characters to CSS-friendly identifiers."""


# ============================================================================
# Finger Visualization
# ============================================================================

FingerDimensions = namedtuple("FingerDimensions", ["height", "width"])
"""Dimensions for finger visualization columns.

Attributes:
    height: Vertical height of the finger column
    width: Horizontal width of the finger column
"""

FINGER_HEIGHTS: Dict[str, FingerDimensions] = {
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
"""Dimensions for each finger's visualization column.

Keys correspond to finger identifiers:
- L1-L4: Left hand fingers (pinky to index)
- R1-R4: Right hand fingers (index to pinky)
- THUMB: Space bar thumb
"""

MAX_FINGER_HEIGHT: int = max(
    dimensions.height for dimensions in FINGER_HEIGHTS.values()
)
"""Maximum height among all finger columns for alignment purposes."""
