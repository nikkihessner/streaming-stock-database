from pathlib import Path
import re

from stock_pipeline.utils.excel_utils import iter_ohlcv_rows


def test_iter_ohlcv_rows_on_real_aapl_file():
    # Locate repo root relative to this test file
    repo_root = Path(__file__).resolve().parents[1]
    data_path = repo_root / "data" / "AAPL.xlsx"

    assert data_path.exists(), f"Test file not found: {data_path}"

    rows = iter_ohlcv_rows(data_path, symbol_hint="AAPL")

    # We don't want to load all 30 years into memory; just sample a few
    sample = []
    for i, row in enumerate(rows):
        sample.append(row)
        if i >= 4:  # first 5 rows max
            break

    assert len(sample) > 0, "Expected at least one row from AAPL.xlsx"

    first = sample[0]

    # Basic shape checks
    assert "symbol" in first
    assert "trade_date" in first
    assert "open" in first
    assert "high" in first
    assert "low" in first
    assert "close" in first
    assert "volume" in first

    # Symbol should match hint (or embedded symbol if your file has that)
    assert first["symbol"] == "AAPL"

    # trade_date should be ISO-ish: YYYY-MM-DD
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", first["trade_date"])

