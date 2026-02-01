# keyboard.py
from enum import Enum


class PhysicalKey(Enum):
    # Number row
    KEY_ESCAPE = 1
    KEY_TILDE = 41
    KEY_1 = 2
    KEY_2 = 3
    KEY_3 = 4
    KEY_4 = 5
    KEY_5 = 6
    KEY_6 = 7
    KEY_7 = 8
    KEY_8 = 9
    KEY_9 = 10
    KEY_0 = 11
    KEY_MINUS = 12
    KEY_EQUAL = 13
    KEY_BACKSPACE = 14

    # Top row
    KEY_TAB = 15
    KEY_Q = 16
    KEY_W = 17
    KEY_E = 18
    KEY_R = 19
    KEY_T = 20
    KEY_Y = 21
    KEY_U = 22
    KEY_I = 23
    KEY_O = 24
    KEY_P = 25
    KEY_LEFT_BRACKET = 26
    KEY_RIGHT_BRACKET = 27
    KEY_BACKSLASH = 43

    # Home row
    KEY_A = 30
    KEY_S = 31
    KEY_D = 32
    KEY_F = 33
    KEY_G = 34
    KEY_H = 35
    KEY_J = 36
    KEY_K = 37
    KEY_L = 38
    KEY_SEMICOLON = 39
    KEY_QUOTE = 40
    KEY_ENTER = 28

    # Bottom row
    KEY_SHIFT_LEFT = 42
    KEY_Z = 44
    KEY_X = 45
    KEY_C = 46
    KEY_V = 47
    KEY_B = 48
    KEY_N = 49
    KEY_M = 50
    KEY_COMMA = 51
    KEY_DOT = 52
    KEY_SLASH = 53
    KEY_SHIFT_RIGHT = 54
    KEY_SPACE = 57


KEYBOARD_ROWS = [
    [
        PhysicalKey.KEY_ESCAPE,
        PhysicalKey.KEY_TILDE,
        PhysicalKey.KEY_1,
        PhysicalKey.KEY_2,
        PhysicalKey.KEY_3,
        PhysicalKey.KEY_4,
        PhysicalKey.KEY_5,
        PhysicalKey.KEY_6,
        PhysicalKey.KEY_7,
        PhysicalKey.KEY_8,
        PhysicalKey.KEY_9,
        PhysicalKey.KEY_0,
        PhysicalKey.KEY_MINUS,
        PhysicalKey.KEY_EQUAL,
        PhysicalKey.KEY_BACKSPACE,
    ],
    [
        PhysicalKey.KEY_TAB,
        PhysicalKey.KEY_Q,
        PhysicalKey.KEY_W,
        PhysicalKey.KEY_E,
        PhysicalKey.KEY_R,
        PhysicalKey.KEY_T,
        PhysicalKey.KEY_Y,
        PhysicalKey.KEY_U,
        PhysicalKey.KEY_I,
        PhysicalKey.KEY_O,
        PhysicalKey.KEY_P,
        PhysicalKey.KEY_LEFT_BRACKET,
        PhysicalKey.KEY_RIGHT_BRACKET,
        PhysicalKey.KEY_BACKSLASH,
    ],
    [
        PhysicalKey.KEY_A,
        PhysicalKey.KEY_S,
        PhysicalKey.KEY_D,
        PhysicalKey.KEY_F,
        PhysicalKey.KEY_G,
        PhysicalKey.KEY_H,
        PhysicalKey.KEY_J,
        PhysicalKey.KEY_K,
        PhysicalKey.KEY_L,
        PhysicalKey.KEY_SEMICOLON,
        PhysicalKey.KEY_QUOTE,
        PhysicalKey.KEY_ENTER,
    ],
    [
        PhysicalKey.KEY_SHIFT_LEFT,
        PhysicalKey.KEY_Z,
        PhysicalKey.KEY_X,
        PhysicalKey.KEY_C,
        PhysicalKey.KEY_V,
        PhysicalKey.KEY_B,
        PhysicalKey.KEY_N,
        PhysicalKey.KEY_M,
        PhysicalKey.KEY_COMMA,
        PhysicalKey.KEY_DOT,
        PhysicalKey.KEY_SLASH,
        PhysicalKey.KEY_SHIFT_RIGHT,
    ],
    [
        PhysicalKey.KEY_SPACE,
    ],
]

FINGER_MAP = {
    # Number row
    # Numbers
    PhysicalKey.KEY_TILDE: "L1",
    PhysicalKey.KEY_1: "L1",
    PhysicalKey.KEY_2: "L2",
    PhysicalKey.KEY_3: "L3",
    PhysicalKey.KEY_4: "L4",
    PhysicalKey.KEY_5: "L4",
    PhysicalKey.KEY_6: "R1",
    PhysicalKey.KEY_7: "R1",
    PhysicalKey.KEY_8: "R2",
    PhysicalKey.KEY_9: "R3",
    PhysicalKey.KEY_0: "R4",
    PhysicalKey.KEY_MINUS: "R4",
    PhysicalKey.KEY_EQUAL: "R4",
    PhysicalKey.KEY_BACKSPACE: "R4",
    # Top row
    PhysicalKey.KEY_TAB: "L1",
    PhysicalKey.KEY_Q: "L1",
    PhysicalKey.KEY_W: "L2",
    PhysicalKey.KEY_E: "L3",
    PhysicalKey.KEY_R: "L4",
    PhysicalKey.KEY_T: "L4",
    PhysicalKey.KEY_Y: "R1",
    PhysicalKey.KEY_U: "R1",
    PhysicalKey.KEY_I: "R2",
    PhysicalKey.KEY_O: "R3",
    PhysicalKey.KEY_P: "R4",
    PhysicalKey.KEY_LEFT_BRACKET: "R4",
    PhysicalKey.KEY_RIGHT_BRACKET: "R4",
    PhysicalKey.KEY_BACKSLASH: "R4",
    # Home row
    PhysicalKey.KEY_A: "L1",
    PhysicalKey.KEY_S: "L2",
    PhysicalKey.KEY_D: "L3",
    PhysicalKey.KEY_F: "L4",
    PhysicalKey.KEY_G: "L4",
    PhysicalKey.KEY_H: "R1",
    PhysicalKey.KEY_J: "R1",
    PhysicalKey.KEY_K: "R2",
    PhysicalKey.KEY_L: "R3",
    PhysicalKey.KEY_SEMICOLON: "R4",
    PhysicalKey.KEY_QUOTE: "R4",
    PhysicalKey.KEY_ENTER: "R4",
    # Bottom row
    PhysicalKey.KEY_SHIFT_LEFT: "L1",
    PhysicalKey.KEY_Z: "L1",
    PhysicalKey.KEY_X: "L2",
    PhysicalKey.KEY_C: "L3",
    PhysicalKey.KEY_V: "L4",
    PhysicalKey.KEY_B: "L4",
    PhysicalKey.KEY_N: "R1",
    PhysicalKey.KEY_M: "R1",
    PhysicalKey.KEY_COMMA: "R2",
    PhysicalKey.KEY_DOT: "R3",
    PhysicalKey.KEY_SLASH: "R4",
    PhysicalKey.KEY_SHIFT_RIGHT: "R4",
    PhysicalKey.KEY_SPACE: "THUMB",
}

# Special Display Labels for Control Keys
DISPLAY_MAP = {
    PhysicalKey.KEY_ESCAPE: "ESC",
    PhysicalKey.KEY_TAB: "TAB",
    PhysicalKey.KEY_BACKSPACE: "BACK",
    PhysicalKey.KEY_ENTER: "ENTER",
    PhysicalKey.KEY_SHIFT_LEFT: "SHIFT",
    PhysicalKey.KEY_SHIFT_RIGHT: "SHIFT",
    PhysicalKey.KEY_SPACE: "SPACE",
    PhysicalKey.KEY_TILDE: "`",  # Explicit override if needed
}

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
