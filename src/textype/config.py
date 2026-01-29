from collections import namedtuple

SHOW_QWERTY = True 
SHOW_FINGERS = True
HARD_MODE = True
SHOW_STATS_ON_END = True

SENTENCES = [
    "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
    "PRACTICE UNTIL THE MOTIONS BECOME SECOND NATURE",
    "RELIANCE ON SIGHT IS THE ENEMY OF SPEED",
    "FLUIDITY MATTERS MORE THAN RAW VELOCITY"
]

ID_MAP = {" ": "space", ";": "semicolon", ",": "comma", ".": "dot", "/": "slash"}

FingerDimensions = namedtuple('FingerDimensions', ['height', 'width'])

FINGER_HEIGHTS = {
    "L1": FingerDimensions(4, 7), "L2": FingerDimensions(6, 7), "L3": FingerDimensions(7, 7), "L4": FingerDimensions(6, 7),
    "THUMB": FingerDimensions(2, 20),
    "R1": FingerDimensions(6, 7), "R2": FingerDimensions(7, 7), "R3": FingerDimensions(6, 7), "R4": FingerDimensions(4, 7)
}

MAX_FINGER_HEIGHT = max(dimensions.height for dimensions in FINGER_HEIGHTS.values())

FINGER_MAP = {
    "Q": "L1", "A": "L1", "Z": "L1",
    "W": "L2", "S": "L2", "X": "L2",
    "E": "L3", "D": "L3", "C": "L3",
    "R": "L4", "F": "L4", "V": "L4",
    "T": "L4", "G": "L4", "B": "L4",
    "Y": "R1", "H": "R1", "N": "R1",
    "U": "R1", "J": "R1", "M": "R1",
    "I": "R2", "K": "R2", ",": "R2",
    "O": "R3", "L": "R3", ".": "R3",
    "P": "R4", ";": "R4", "/": "R4",
    " ": "THUMB"
}
