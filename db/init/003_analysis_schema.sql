CREATE TYPE wave_structure_type AS ENUM (
    'IMPULSE',
    'DIAGONAL',
    'CORRECTIVE',
    'REGULAR FLAT',
    'RUNNING FLAT', 
    'EXPANDED FLAT',
    'EXPANDING TRIANGLE',
    'CONTRACTING TRIANGLE'
);

CREATE TYPE wave_trend_direction AS ENUM (
    'UP',
    'DOWN'
);

CREATE TABLE IF NOT EXISTS analysis_wave_history (
    id              uuid PRIMARY KEY DEFAULT uuidv7(),

    symbol          text                NOT NULL,
    candle_date     date                NOT NULL,

    -- FK back to OHLCV (assuming UNIQUE(symbol, candle_date, ...) exists)
    CONSTRAINT analysis_wave_history_ohlcv_fk
        FOREIGN KEY (symbol, candle_date)
        REFERENCES ohlcv (symbol, candle_date),
    
    -- Derived price features
    delta_price     double precision    NOT NULL,
    velocity        double precision,
    momentum        double precision,
    delta_momentum  double precision,

    -- Metadata
    day_of_week     smallint            NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    sector          equity_sector       NOT NULL DEFAULT 'OTHER',

    -- Wave/structure classification at this candle
    structure_type
)

