from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterator, Optional

import pandas as pd

from stock_pipeline.utils.file_utils import derive_symbol
from utils.logging_config import get_logger

log = get_logger("excel_utils")


def to_iso_date(value) -> str:
    """
    Normalize a value that might be:
      - pandas.Timestamp
      - datetime / date
      - Excel serial number (float/int, days since 1899-12-30)
      - string

    and return an ISO date string "YYYY-MM-DD".
    """
    if pd.isna(value):
        raise ValueError("Date value is NaN/NA, cannot convert to ISO date")

    # Already datetime-like
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    # Excel serial number (float or int). Excel dates start on 1899-12-30.
    if isinstance(value, (int, float)):
        try:
            ts = pd.to_datetime(value, unit="D", origin="1899-12-30")
            return ts.date().isoformat()
        except Exception as exc:
            raise ValueError(f"Failed to parse Excel serial date {value!r}: {exc}") from exc

    # Fallback: try to parse as string
    try:
        ts = pd.to_datetime(value)
        return ts.date().isoformat()
    except Exception as exc:
        raise ValueError(f"Failed to parse Excel serial date {value!r}:{exc}") from exc

def iter_ohlcv_rows(
    path: Path,
    symbol_hint: Optional[str] = None,
) -> Iterator[Dict[str, object]]:
    """
    Yield dicts with:
      symbol, trade_date (ISO string), open, high, low, close, volume
    from a single Excel file.

    Expected columns (case-insensitive, whitespace ignored):
      Date, Open, High, Low, Close, Volume
    Optionally:
      Symbol
    """
    log.info("Reading OHLCV rows from %s", path)

    # Use openpyxl so behavior is consistent
    df = pd.read_excel(path, engine="openpyxl")

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

    # --- Symbol column handling ---
    if "symbol" in normalized:
        symbol_col = normalized["symbol"]
    else:
        # No Symbol column in the file → derive it
        symbol = derive_symbol(path) or symbol_hint
        if not symbol:
            log.error(
                "File %s has no Symbol column and no symbol_hint was provided", path
            )
            raise ValueError(
                f"File {path} has no Symbol column and no symbol_hint was provided."
            )

        df["Symbol"] = symbol
        normalized["symbol"] = "Symbol"
        symbol_col = normalized["symbol"]

    # Cache resolved column names
    date_col = normalized["date"]
    open_col = normalized["open"]
    high_col = normalized["high"]
    low_col = normalized["low"]
    close_col = normalized["close"]
    volume_col = normalized["volume"]

    # --- Iterate rows ---
    for i, (_, row) in enumerate(df.iterrows()):
        try:
            date_val = row[date_col]
            volume_val = row[volume_col]

            if pd.isna(date_val) or pd.isna(volume_val):
                log.warning(
                    "Skipping row %s in %s due to NaN requried fields (date=%r volume=%s)",
                    i,
                    path.name,
                    date_val,
                    volume_val
                )
                continue
            
            symbol_val = str(row[symbol_col]).strip()
            trade_date_iso = to_iso_date(date_val)

            yield {
                "symbol": symbol_val,
                "trade_date": trade_date_iso,
                "open": float(row[open_col]),
                "high": float(row[high_col]),
                "low": float(row[low_col]),
                "close": float(row[close_col]),
                "volume": int(volume_val),
            }

        except ValueError as exc:
            log.warning(
                "Skipping row %s in %s due to parse error: %s",
                i,
                path.name,
                exc,
            )
            continue

        except Exception:
            # Log and re-raise so the caller can decide what to do
            log.exception("Unexpected failure parsing row %s in file %s", 
                i,
                path.name,
            )
            continue