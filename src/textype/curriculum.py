from typing import List, Tuple, TypedDict
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
            LessonDict(
                name=f"{idx}.1: Isolation",
                algo="repeat",
                row=row,
                target_acc=95,
                target_wpm=10,
                shift_mode="off",
            ),
            LessonDict(
                name=f"{idx}.2: Adjacency",
                algo="adjacent",
                row=row,
                target_acc=95,
                target_wpm=10,
                shift_mode="off",
            ),
            LessonDict(
                name=f"{idx}.3: Alternating",
                algo="alternating",
                row=row,
                target_acc=92,
                target_wpm=10,
                shift_mode="off",
            ),
            LessonDict(
                name=f"{idx}.4: Mirroring",
                algo="mirror",
                row=row,
                target_acc=92,
                target_wpm=10,
                shift_mode="off",
            ),
            LessonDict(
                name=f"{idx}.5: Rolling",
                algo="rolls",
                row=row,
                target_acc=90,
                target_wpm=10,
                shift_mode="off",
            ),
            LessonDict(
                name=f"{idx}.6: Synthesis",
                algo="pseudo",
                row=row,
                target_acc=95,
                target_wpm=10,
                shift_mode="off",
            ),
            LessonDict(
                name=f"{idx}.7: Mixed Case",
                algo="pseudo",
                row=row,
                target_acc=90,
                target_wpm=10,
                shift_mode="mixed",
            ),
        ]
    )

# Foundation lessons (lesson numbers 2-12)
foundation_lessons = [
    LessonDict(
        name="2.1: Isolation",
        algo="repeat",
        row="focus_e_i",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="2.2: Variation",
        algo="pseudo",
        row="focus_e_i",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="3.1: Isolation",
        algo="repeat",
        row="focus_r_u",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="3.2: Variation",
        algo="pseudo",
        row="focus_r_u",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="4.1: Isolation",
        algo="repeat",
        row="focus_t_o",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="4.2: Variation",
        algo="pseudo",
        row="focus_t_o",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="5.1: Isolation",
        algo="repeat",
        row="focus_shift_period",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="5.2: Variation",
        algo="pseudo",
        row="focus_shift_period",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="6.1: Isolation",
        algo="repeat",
        row="focus_c_comma",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="6.2: Variation",
        algo="pseudo",
        row="focus_c_comma",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="7.1: Isolation",
        algo="repeat",
        row="focus_g_h",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="7.2: Variation",
        algo="pseudo",
        row="focus_g_h",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="8.1: Isolation",
        algo="repeat",
        row="focus_v_n_slash",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="8.2: Variation",
        algo="pseudo",
        row="focus_v_n_slash",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="9.1: Isolation",
        algo="repeat",
        row="focus_w_m",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="9.2: Variation",
        algo="pseudo",
        row="focus_w_m",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="10.1: Isolation",
        algo="repeat",
        row="focus_q_p",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="10.2: Variation",
        algo="pseudo",
        row="focus_q_p",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="11.1: Isolation",
        algo="repeat",
        row="focus_b_y",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="11.2: Variation",
        algo="pseudo",
        row="focus_b_y",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
    LessonDict(
        name="12.1: Isolation",
        algo="repeat",
        row="focus_z_x",
        target_acc=95,
        target_wpm=10,
        shift_mode="off",
    ),
    LessonDict(
        name="12.2: Variation",
        algo="pseudo",
        row="focus_z_x",
        target_acc=95,
        target_wpm=10,
        shift_mode="mixed",
    ),
]

LESSONS.extend(foundation_lessons)

# Numbers row lessons (13.1-13.2)
LESSONS.extend(
    [
        LessonDict(
            name="13.1: Numbers Isolation",
            algo="repeat",
            row="numbers",
            target_acc=95,
            target_wpm=10,
            shift_mode="off",
        ),
        LessonDict(
            name="13.2: Numbers Variation",
            algo="pseudo",
            row="numbers",
            target_acc=95,
            target_wpm=10,
            shift_mode="off",
        ),
    ]
)

# Keep symbols lessons (14.1-14.3)
LESSONS.extend(
    [
        LessonDict(
            name="14.1: Special Symbols",
            algo="repeat",
            row="symbols_basic",
            target_acc=90,
            target_wpm=10,
            shift_mode="mixed",
        ),
        LessonDict(
            name="14.2: Symbols Adjacency",
            algo="adjacent",
            row="symbols_basic",
            target_acc=90,
            target_wpm=10,
            shift_mode="mixed",
        ),
        LessonDict(
            name="14.3: Symbols Synthesis",
            algo="pseudo",
            row="symbols_basic",
            target_acc=90,
            target_wpm=10,
            shift_mode="mixed",
        ),
    ]
)

# Sentence practice lessons (15.1-15.3)
LESSONS.extend(
    [
        LessonDict(
            name="15.1: Sentence Practice I",
            algo="sentence",
            row="home",
            target_acc=90,
            target_wpm=20,
            shift_mode="off",
        ),
        LessonDict(
            name="15.2: Sentence Practice II",
            algo="sentence",
            row="home",
            target_acc=92,
            target_wpm=25,
            shift_mode="off",
        ),
        LessonDict(
            name="15.3: Sentence Practice III",
            algo="sentence",
            row="home",
            target_acc=95,
            target_wpm=30,
            shift_mode="off",
        ),
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
    "Typing speed improves with consistent daily practice",
    "Accuracy first, speed will follow naturally",
    "Keep your eyes on the screen, not the keyboard",
    "Proper finger placement is key to efficient typing",
    "Every expert was once a beginner who kept practicing",
    "Slow and steady wins the typing race",
    "Muscle memory develops through repetition and focus",
    "The home row is your foundation for touch typing",
    "Challenge yourself with new words and patterns",
    "Take breaks to avoid fatigue and maintain accuracy",
    "Celebrate small improvements along the way",
]
"""Default practice sentences for non-lesson typing."""
