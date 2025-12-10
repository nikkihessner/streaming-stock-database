from datetime import datetime
from uuid import UUID, uuid4

from stock_analysis.datamodels import (
    CandleRaw,
    CandleFeatures,
    WaveSegment,
    WaveStructureState,
    Prediction,
    PredictionGrid,
    LabeledCandleRow,
)


def _now():
    return datetime(2020, 1, 1, 12, 0)


# --- Candle-level ------------------------------------------------------------

def test_candle_raw_creation():
    ts = _now()
    c = CandleRaw(
        symbol="AAPL",
        timestamp=ts,
        open=100.0,
        high=110.0,
        low=95.0,
        close=105.0,
        volume=123456,
    )
    assert c.symbol == "AAPL"
    assert c.close == 105.0
    assert isinstance(c.timestamp, datetime)


def test_candle_features_creation():
    ts = _now()
    f = CandleFeatures(
        symbol="AAPL",
        timestamp=ts,
        open=100.0,
        high=110.0,
        low=95.0,
        close=105.0,
        volume=123456,
        delta_price=5.0,
        velocity=10.0,
        momentum=200.0,
        delta_momentum=50.0,
        day_of_week=2,
        sector="TECH",
    )
    assert f.delta_price == 5.0
    assert f.velocity == 10.0
    assert f.sector == "TECH"


# --- Wave / Structure --------------------------------------------------------

def test_wave_segment_basic():
    start = _now()
    end = _now()

    w = WaveSegment(
        symbol="AAPL",
        wave_label="1",
        wave_index=1,
        direction="UP",
        start_idx=0,
        end_idx=5,
        start_time=start,
        end_time=end,
        min_price=95.0,
        max_price=110.0,
        proportion_of_parent=1.0,
    )

    assert w.wave_label == "1"
    assert w.direction == "UP"
    assert w.min_price == 95.0
    assert w.max_price == 110.0


def test_wave_structure_state_creation():
    start = _now()
    end = _now()

    struct_id = uuid4()
    wave = WaveSegment(
        symbol="AAPL",
        wave_label="1",
        wave_index=1,
        direction="UP",
        start_idx=0,
        end_idx=5,
        start_time=start,
        end_time=end,
        min_price=95.0,
        max_price=110.0,
    )

    s = WaveStructureState(
        structure_id=struct_id,
        symbol="AAPL",
        timeframe="1D",
        structure_type="IMPULSE",
        trend_direction="UP",
        start_idx=0,
        end_idx=5,
        start_time=start,
        end_time=end,
        min_price=95.0,
        max_price=110.0,
        waves=[wave],
        is_complete=False,
    )

    assert s.structure_id == struct_id
    assert s.structure_type == "IMPULSE"
    assert len(s.waves) == 1


# --- Predictions -------------------------------------------------------------

def test_prediction_and_grid():
    ts = _now()
    p = Prediction(
        target_price=120.0,
        confidence=0.8,
        target_time=ts,
        scenario_label="impulse_wave5",
    )
    grid = PredictionGrid(
        symbol="AAPL",
        timeframe="1D",
        structure_type="IMPULSE",
        as_of=ts,
        predictions=(p,),
    )

    assert len(grid.predictions) == 1
    assert grid.predictions[0].confidence == 0.8


# --- Labeled Candle Row ------------------------------------------------------

def test_labeled_candle_row_minimal():
    ts = _now()
    row = LabeledCandleRow(
        symbol="AAPL",
        timestamp=ts,
        open=100.0,
        high=110.0,
        low=95.0,
        close=105.0,
        volume=99999,
        structure_id=uuid4(),
        structure_type="IMPULSE",
        wave_label="3",
        wave_index=3,
        wave_min_price=100.0,
        wave_max_price=108.0,
        pattern_mask=0b10101010,
        active_scenario_label="impulse_wave5",
        active_target_price=130.0,
        active_confidence=0.7,
    )

    assert row.symbol == "AAPL"
    assert row.wave_label == "3"
    assert row.wave_max_price == 108.0
    assert row.pattern_mask == 0b10101010
    assert row.active_confidence == 0.7