DROP TABLE IF EXISTS ohlcv CASCADE;

CREATE TABLE IF NOT EXISTS ohlcv (
    id               uuid NOT NULL DEFAULT uuidv7(),

    symbol           TEXT             NOT NULL,
    candle_date      DATE             NOT NULL,
    candle_open      DOUBLE PRECISION NOT NULL,
    candle_high      DOUBLE PRECISION NOT NULL,
    candle_low       DOUBLE PRECISION NOT NULL,
    candle_close     DOUBLE PRECISION NOT NULL,
    candle_volume    BIGINT           NOT NULL,
    file_id          uuid             NOT NULL,
    row_index        INTEGER,
    ingested_at      TIMESTAMPTZ      NOT NULL DEFAULT now(),

    PRIMARY KEY (symbol, candle_date, id),

    CONSTRAINT ohlcv_unique_row UNIQUE (symbol, candle_date, file_id, row_index),

    CONSTRAINT ohlcv_volume_nonnegative CHECK (candle_volume >= 0),
    CONSTRAINT ohlcv_prices_nonnegative CHECK (
        candle_open  >= 0 AND
        candle_high  >= 0 AND
        candle_low   >= 0 AND
        candle_close >= 0
    ),
    CONSTRAINT ohlcv_high_ge_low CHECK (candle_high >= candle_low),
    CONSTRAINT ohlcv_candle_date_reasonable CHECK (candle_date >= DATE '1900-01-01')
)
PARTITION BY HASH (symbol);

DO $$
DECLARE
    b int;
    modulus int := 64;  -- 👈 reduced
BEGIN
    FOR b IN 0..modulus-1 LOOP
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS ohlcv_s%s
                PARTITION OF ohlcv
                FOR VALUES WITH (MODULUS %s, REMAINDER %s)
                PARTITION BY RANGE (candle_date);',
            b, modulus, b
        );
    END LOOP;
END $$;

DO $$
DECLARE
    y int;
    b int;
    modulus int := 64;  -- 👈 match above
BEGIN
    FOR b IN 0..modulus-1 LOOP
        FOR y IN 1990..2030 LOOP   -- could also start with 2000..2025
            EXECUTE format(
                'CREATE TABLE IF NOT EXISTS ohlcv_s%s_y%s
                    PARTITION OF ohlcv_s%s
                    FOR VALUES FROM (%L) TO (%L);',
                b, y, b,
                make_date(y,1,1),
                make_date(y+1,1,1)
            );
        END LOOP;
    END LOOP;
END $$;

CREATE INDEX IF NOT EXISTS ohlcv_symbol_date_idx
    ON ohlcv (symbol, candle_date);

CREATE INDEX IF NOT EXISTS ohlcv_candle_date_idx
    ON ohlcv (candle_date);

CREATE INDEX IF NOT EXISTS ohlcv_desc_symbol_date_idx
    ON ohlcv (symbol, candle_date DESC);