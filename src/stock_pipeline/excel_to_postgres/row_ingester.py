import json
import os
import signal
from dataclasses import dataclass
from typing import List, Optional

import psycopg
from confluent_kafka import Message

from stock_pipeline.config import TOPICS
from utils.kafka_utils import create_consumer, create_producer
from utils.logging_config import get_logger

log = get_logger("row_ingester")

GROUP_ID = "row-ingester"

BATCH_SIZE = 500
POLL_TIMEOUT_SEC = 1.0

@dataclass
class IngestRow:
    symbol: str
    candle_date: str
    candle_open: float
    candle_high: float
    candle_low: float
    candle_close: float
    candle_volume: int
    file_id: str
    row_index: int

def _get_db_password_from_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def _create_db_connection():
    """
    Create a Postgres connection using environment variables.
    
    Uses:
      PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD_FILE
    """
    host = os.environ.get("PGHOST", "localhost")
    port = int(os.environ.get("PGPORT", "5432"))
    dbname = os.environ.get("PGDATABASE", "postgres")
    user = os.environ.get("PGUSER", "postgres")
    password_file = os.environ.get("PGPASSWORD_FILE")

    if not password_file:
        raise RuntimeError("PGPASSWORD_FILE must be set for row_ingester")
    
    password = _get_db_password_from_file(password_file)

    log.info(
        "Connecting to Postgres host=%s port=%s dbname=%s user=%s",
        host,
        port,
        dbname,
        user,
    )

    conn = psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        autocommit=False,
    )
    return conn

def _parse_row_message(msg: Message) -> IngestRow:
    """
    Decode a kafka message from rows_to_process into an IngestRow.

    Expected JSON payload:
        {
          "file_id": "...",
          "row_index": 123,
          "symbol": "AAPL",
          "trade_date": "YYYY-MM-DD",
          "open": ...,
          "high": ...,
          "low": ...,
          "close": ...,
          "volume": ...
        }
    """
    raw_value = msg.value()
    if raw_value is None:
        log.error("Received row message with no value: %s", msg)
        raise ValueError("Received row message with no value")
    
    try:
        data = json.loads(raw_value.decode("utf-8"))
    except Exception as e:
        log.error("Failed to decode JSON from rows_to_process: %s", e, exc_info=True)
        raise

    required = [
        "file_id",
        "row_index",
        "symbol",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        log.error(
            "Row message missing keys %s. Got payload: %s",
            missing,
            data,
        )
        raise ValueError(f"Row message missing keys: {missing}")
    
    return IngestRow(
        symbol=str(data["symbol"]),
        candle_date=str(data["trade_date"]),
        candle_open=float(data["open"]),
        candle_high=float(data["high"]),
        candle_low=float(data["low"]),
        candle_close=float(data["close"]),
        candle_volume=int(data["volume"]),
        file_id=str(data["file_id"]),
        row_index=int(data["row_index"]),
    )

def _insert_batch(conn, rows: List[IngestRow]) -> None:
    """
    Insert a batch of rows into ohlcv using parameterized SQL.

    Uses ON CONFLICT DO NOTHING on the unique constraint so replays are safe.
    """
    if not rows:
        return

    sql = """
        INSERT INTO ohlcv (
            symbol,
            candle_date,
            candle_open,
            candle_high,
            candle_low,
            candle_close,
            candle_volume,
            file_id,
            row_index
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (symbol, candle_date, file_id, row_index)
        DO NOTHING;
    """

    params = [
        (
            r.symbol,
            r.candle_date,
            r.candle_open,
            r.candle_high,
            r.candle_low,
            r.candle_close,
            r.candle_volume,
            r.file_id,
            r.row_index,
        )
        for r in rows
    ]

    with conn.cursor() as cur:
        cur.executemany(sql, params)

    log.info("Inserted batch of %s rows into ohlcv", len(rows))

def _send_to_dlq(dlq_producer, msg: Message, reason: str) -> None:
    """
    Send the original message to the DLQ with a reason field.
    """
    try:
        payload = {
            "reason": reason,
            "topic": msg.topic(),
            "partition": msg.partition(),
            "offset": msg.offset(),
            "key": msg.key().decode("utf-8") if msg.key() else None,
            "value": msg.value().decode("utf-8") if msg.value() else None,
        }

        dlq_key = f"{msg.topic()}:{msg.partition()}:{msg.offset()}"

        dlq_producer.produce(
            TOPICS.ROWS_DLQ,
            key=dlq_key.encode("utf-8"),
            value=json.dumps(payload).encode("utf-8"),
        )
        dlq_producer.flush()
        log.warning(
            "Sent message to DLQ topic=%s reason=%s offset=%s",
            TOPICS.ROWS_DLQ,
            reason,
            msg.offset(),
        )
    except Exception:
        log.exception("Failed to send message to DLQ")

def _graceful_shutdown(consumer):
    log.info("Shutting down row_ingester consumer...")
    try:
        consumer.close()
    except Exception:
        log.exception("Error while closing consumer")
    log.info("Shutdown complete.")

def main() -> None:
    log.info("Starting row_ingester. Subscribing to topic %s", TOPICS.ROWS_TO_PROCESS)

    consumer = create_consumer(
        group_id=GROUP_ID,
        client_id="row_ingester",
    )
    dlq_producer = create_producer(client_id="row_ingester_dlq")

    conn = _create_db_connection()

    running = True

    def handle_signal(signum, frame):
        nonlocal running
        log.info("Received signal %s, requesting shutdown...", signum)
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    consumer.subscribe([TOPICS.ROWS_TO_PROCESS])

    try:
        batch: List[IngestRow] = []
        last_msg: Optional[Message] = None

        while running:
            msg = consumer.poll(timeout=POLL_TIMEOUT_SEC)
            if msg is None:
                if batch:
                    try:
                        _insert_batch(conn, batch)
                        conn.commit()
                        
                        with conn.cursor() as cur:
                            cur.execute("SELECT COUNT(*) FROM ohlcv;")
                            count = cur.fetchone()[0]
                        log.info("After batch commit, ohlcv row count = %s", count)
                        if last_msg is not None:
                            try:
                                consumer.commit(message=last_msg)
                            except Exception:
                                log.exception("Failed to commit offset after batch insert.")
                        batch.clear()
                        last_msg = None
                    except Exception:
                        log.exception("Failed to insert batch; rolling back")
                        conn.rollback()
                continue

            if msg.error():
                log.error("Consumer error: %s", msg.error())
                continue

            try:
                row = _parse_row_message(msg)
                batch.append(row)
                last_msg = msg
            except Exception as e:
                log.error(
                    "Failed to parse row message from %s; sending to DLQ and skipping",
                    msg.topic(),
                    exc_info=True,
                )
                _send_to_dlq(dlq_producer, msg, reason=f"parse_error: {e}")
                try:
                    consumer.commit(message=msg)
                except Exception:
                    log.exception("Failed to commit offset for bad message")
                continue

            if len(batch) >= BATCH_SIZE:
                try:
                    _insert_batch(conn, batch)
                    conn.commit()
                    if last_msg is not None:
                        consumer.commit(message=last_msg)
                    batch.clear()
                    last_msg = None
                except Exception:
                    log.exception("Failed to insert batch; rolling back")
                    conn.rollback()
        
        # On shutdown, flush any remaining batch
        if batch:
            try: 
                _insert_batch(conn, batch)
                conn.commit()
                if last_msg is not None:
                    try:
                        consumer.commit(message=last_msg)
                    except Exception:
                        log.exception("Failed to commit offset for final batch")
            except Exception:
                log.exception("Failed to insert final batch during shutdown")
                conn.rollback()
    finally:
        _graceful_shutdown(consumer)
        try:
            conn.commit()
            conn.close()
        except Exception:
            log.exception("Error closing DB connection")

if __name__ == "__main__":
    main()


