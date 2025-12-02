from utils.logging_config import get_logger
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, List, Any, ByteString
from heuristics import impulse, diagonal, zigzag, run_flat, reg_flat, expand_flat, contracting_tri, expanding_tri

log = get_logger("heuristics")
wave_counts = ["ONE", "TWO", "THREE", "FOUR", "FIVE"]

# if bitmask for structure is good, run its heuristics for that wave count

def run_heuristics(alive_bitmask: ByteString) -> ByteString:
    impulse(alive_bitmask)
    diagonal(alive_bitmask)
