from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import pandas as pd

from stock_pipeline.utils.file_utils import derive_symbol
from utils.logging_config import get_logger


def iter_ohlcv_rows(
    path: Path,
    symbol_hint: Optional[str] = None,
) -> Iterator[Dict[str, object]]:
    """
    Yield dicts with symbol, trade_date (ISO string), open, high, low, close, volume
    from a single Excel file.

    Expected columns (case-insensitive, whitespace ignored):
        Date, Open, High, Low, Close, Volume
      Optionally:
        Symbol
    """
    log = get_logger("excel_utils")
    df = pd.read_excel(path)

    # Normalize column names (case-insensitive mapping)
    normalized = {c.lower().strip(): c for c in df.columns}

    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in normalized]

    if missing:
        log.error(
            "File %s missing required columns %s. Found: %s",
            path,
            missing,
            list(df.columns),
        )
        raise ValueError(
            f"File {path} is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    # Symbol column handling
    if "symbol" in normalized:
        symbol_col = normalized["symbol"]
    else:
        # No symbol column → derive it
        symbol = derive_symbol(path)
        if not symbol and not symbol_hint:
            log.error("File %s has no Symbol column and no symbol_hint was provided.", path)
            raise ValueError(
                f"File {path} has no Symbol column and no symbol_hint provided."
            )
        df["Symbol"] = symbol or symbol_hint
        normalized["symbol"] = "Symbol"
        symbol_col = "Symbol"

    # Iterate rows
    try:
        for i, row in df.iterrows():
            # Extract symbol
            symbol = str(row[symbol_col]).strip()

            # Extract date → ISO
            date_val = row[normalized["date"]]
            if hasattr(date_val, "date"):
                trade_date_iso = date_val.date().isoformat()
            else:
                trade_date_iso = str(date_val)

            yield {
                "symbol": symbol,
                "trade_date": trade_date_iso,
                "open": float(row[normalized["open"]]),
                "high": float(row[normalized["high"]]),
                "low": float(row[normalized["low"]]),
                "close": float(row[normalized["close"]]),
                "volume": int(row[normalized["volume"]]),
            }
    except Exception as e:
        log.exception("Unexpected failure parsing row %s in file %s", i, path)