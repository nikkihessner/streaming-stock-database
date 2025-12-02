from enum import Enum, auto

class PatternId(Enum):
    IMPULSE = auto()
    DIAGONAL = auto()
    ZIGZAG = auto()
    RUNNING_FLAT = auto()
    REGULAR_FLAT = auto()
    EXPANDED_FLAT = auto()
    CONTRACTING_TRIANGLE = auto()
    EXPANDING_TRIANGLE = auto()

PATTERN_BITS = {p: i for i, p in enumerate(PatternId)}
ALL_PATTERNS_MASK = (1 << len(PatternId)) - 1