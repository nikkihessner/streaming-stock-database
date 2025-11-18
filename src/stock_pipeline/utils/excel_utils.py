from pathlib import Path
from typing import Dict, Iterator, Optional

import pandas as pd

from stock_pipeline.utils.file_utils import derive_symbol

def iter_ohlcv_rows(path: Path, symbol_hint: Optional[str] = None) -> Iterator[Dict[str, object]]:
    """
    Yield dicts with symbol, trade_date (ISO string), open, high, low, close, volume
    from a single Excel file.

    Expected columns (case-insensitive, whitespace ignored):
        Date, Open, High, Low, Close, Volume
      Optionally:
        Symbol
    
    If the file does not contain a Symbol column, 'symbol_hint'
    (e.g. from the filename) will be used for every row.
    """
    df = pd.read_excel(path)

    symbol = derive_symbol(path)

    # Normalize column names
    normalized = {c.lower().strip(): c for c in df.columns}

    required_columns = ["date", "open", "high", "low", "close", "volume"]
    has_symbol = "symbol" in normalized

    # Validate required columns
    missing = [c for c in required_columns if c not in normalized]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    