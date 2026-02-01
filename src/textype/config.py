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
    shift_mode: str  # "off" (default), "mixed", "always"


rows: Tuple[str, ...] = ("home",)
"""Available keyboard rows for lessons."""

LESSONS: List[LessonDict] = []
"""List of all typing lessons with progression logic."""

# Home row lessons (7 sub-lessons) as per original
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
            {
                "name": f"{idx}.7: Mixed Case",
                "algo": "pseudo",
                "row": row,
                "target_acc": 90,
                "target_wpm": 10,
                "shift_mode": "mixed",
            },
        ]
    )


# Foundation lessons (lesson numbers 2-12)
foundation_lessons = [
    # Lesson 2: E and I
    {
        "name": "2.1: Isolation",
        "algo": "repeat",
        "row": "focus_e_i",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "2.2: Variation",
        "algo": "pseudo",
        "row": "focus_e_i",
        "target_acc": 95,
        "target_wpm": 10,
    },
    # Lesson 3: R and U
    {
        "name": "3.1: Isolation",
        "algo": "repeat",
        "row": "focus_r_u",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "3.2: Variation",
        "algo": "pseudo",
        "row": "focus_r_u",
        "target_acc": 95,
        "target_wpm": 10,
    },
    # Lesson 4: T and O
    {
        "name": "4.1: Isolation",
        "algo": "repeat",
        "row": "focus_t_o",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "4.2: Variation",
        "algo": "pseudo",
        "row": "focus_t_o",
        "target_acc": 95,
        "target_wpm": 10,
    },
    # Lesson 5: Shift & Period
    {
        "name": "5.1: Isolation",
        "algo": "repeat",
        "row": "focus_shift_period",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    {
        "name": "5.2: Variation",
        "algo": "pseudo",
        "row": "focus_shift_period",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    # Lesson 6: C and Comma
    {
        "name": "6.1: Isolation",
        "algo": "repeat",
        "row": "focus_c_comma",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "6.2: Variation",
        "algo": "pseudo",
        "row": "focus_c_comma",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    # Lesson 7: G and H
    {
        "name": "7.1: Isolation",
        "algo": "repeat",
        "row": "focus_g_h",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "7.2: Variation",
        "algo": "pseudo",
        "row": "focus_g_h",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    # Lesson 8: V and N and ?
    {
        "name": "8.1: Isolation",
        "algo": "repeat",
        "row": "focus_v_n_slash",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "8.2: Variation",
        "algo": "pseudo",
        "row": "focus_v_n_slash",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    # Lesson 9: W and M
    {
        "name": "9.1: Isolation",
        "algo": "repeat",
        "row": "focus_w_m",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "9.2: Variation",
        "algo": "pseudo",
        "row": "focus_w_m",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    # Lesson 10: Q and P
    {
        "name": "10.1: Isolation",
        "algo": "repeat",
        "row": "focus_q_p",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "10.2: Variation",
        "algo": "pseudo",
        "row": "focus_q_p",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    # Lesson 11: B and Y
    {
        "name": "11.1: Isolation",
        "algo": "repeat",
        "row": "focus_b_y",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "11.2: Variation",
        "algo": "pseudo",
        "row": "focus_b_y",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
    # Lesson 12: Z and X
    {
        "name": "12.1: Isolation",
        "algo": "repeat",
        "row": "focus_z_x",
        "target_acc": 95,
        "target_wpm": 10,
    },
    {
        "name": "12.2: Variation",
        "algo": "pseudo",
        "row": "focus_z_x",
        "target_acc": 95,
        "target_wpm": 10,
        "shift_mode": "mixed",
    },
]

LESSONS.extend(foundation_lessons)

# Numbers row lessons (13.1-13.2)
LESSONS.extend(
    [
        {
            "name": "13.1: Numbers Isolation",
            "algo": "repeat",
            "row": "numbers",
            "target_acc": 95,
            "target_wpm": 10,
        },
        {
            "name": "13.2: Numbers Variation",
            "algo": "pseudo",
            "row": "numbers",
            "target_acc": 95,
            "target_wpm": 10,
        },
    ]
)

# Keep symbols lessons (14.1-14.3)
LESSONS.extend(
    [
        {
            "name": "14.1: Special Symbols",
            "algo": "repeat",
            "row": "symbols_basic",
            "target_acc": 90,
            "target_wpm": 10,
            "shift_mode": "mixed",
        },
        {
            "name": "14.2: Symbols Adjacency",
            "algo": "adjacent",
            "row": "symbols_basic",
            "target_acc": 90,
            "target_wpm": 10,
            "shift_mode": "mixed",
        },
        {
            "name": "14.3: Symbols Synthesis",
            "algo": "pseudo",
            "row": "symbols_basic",
            "target_acc": 90,
            "target_wpm": 10,
            "shift_mode": "mixed",
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
