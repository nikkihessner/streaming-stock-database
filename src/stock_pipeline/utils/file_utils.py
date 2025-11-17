from datetime import datetime, timezone
from pathlib import Path
import uuid
from typing import Iterable, List, Dict, Union 

PathLike = Union[str, Path]

def list_xlsx_files(directory: PathLike) -> List[Path]:
    """
    Return a list of *.xlsx files in the given directory
    """
    dir_path = Path(directory)
    return sorted(p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() == ".xlsx")

def derive_symbol(filename: PathLike) -> str:
    """
    Take a filename like 'AAPL.xlsx' or 'AAPL_20250101.xlsx and return 'AAPL'.
    """
    name = Path(filename).stem 
    symbol = name.split("_", 1)[0]
    return symbol.upper()

def generate_file_id() -> str:
    """
    Generate a UUID string for a file event. 
    """
    return str(uuid.uuid4())

def build_file_metadata(path: PathLike, symbol: str | None = None) -> Dict[str, object]:
    """
    Build the dict for sending to Kafka.
    """
    p = Path(path)
    if symbol is None:
        symbol =  derive_symbol(p)

    return {
        "file_id": generate_file_id(),
        "path": str(p.name),
        "symbol_hint": symbol,
        "discovered_at": datetime.now(timezone.utc).isoformat(),
    }

