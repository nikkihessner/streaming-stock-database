CREATE TABLE IF NOT EXISTS prices_daily (
    id          uuid   PRIMARY KEY DEFAULT uuidv7(),
    
    symbol      TEXT        NOT NULL,
    trade_date  DATE        NOT NULL,
    
    trade_open  NUMERIC(18,6) NOT NULL,
    high        NUMERIC(18,6) NOT NULL,
    low         NUMERIC(18,6) NOT NULL,
    trade_close NUMERIC(18,6) NOT NULL,
    volume      BIGINT      NOT NULL,
    
    source_file TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE (symbol, trade_date)
);