HARD_MODE = True

SENTENCES = [
    "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
    "PRACTICE UNTIL THE MOTIONS BECOME SECOND NATURE",
    "RELIANCE ON SIGHT IS THE ENEMY OF SPEED",
    "FLUIDITY MATTERS MORE THAN RAW VELOCITY"
]

ID_MAP = {" ": "space", ";": "semicolon", ",": "comma", ".": "dot", "/": "slash"}

FINGER_HEIGHTS = {
    "L1": 4, "L2": 6, "L3": 7, "L4": 6,
    "THUMB": 2,
    "R1": 6, "R2": 7, "R3": 6, "R4": 4
}

MAX_FINGER_HEIGHT = max(FINGER_HEIGHTS.values())

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
