import json
import signal
import sys
from pathlib import Path
from typing import Dict, Any

from confluent_kafka import Message

from utils.kafka_utils import create_producer, create_consumer
from stock_pipeline.utils.excel_utils import iter_ohlcv_rows
from utils.logging_config import get_logger
from stock_pipeline.config import TOPICS

log = get_logger("row_atomizer")

DATA_DIR = Path("/app/data")  # matches your Docker volume

FILES_TOPIC = TOPICS.FILES_TO_PROCESS
ROWS_TOPIC = TOPICS.ROWS_TO_PROCESS
DLQ_TOPIC = TOPICS.ROWS_DLQ
GROUP_ID = "row-atomizer"

def _parse_file_metadata(msg: Message) -> Dict[str, Any]:
    raw_data = msg.value()

    if raw_data is None:
        log.error("Received message with no value")
        raise ValueError("Received message with no value")
    
    try: 
        meta = json.loads(raw_data.decode("utf-8"))
    except Exception as e:
        log.error("Failed to decode JSON from %s: %s", FILES_TOPIC, e, exc_info=True)
        raise

    required_keys = ["file_id", "path"]
    missing = [k for k in required_keys if k not in meta]

    if missing:
        log.error("File metadata missing keys:%s. Got %s", missing, meta)
        raise ValueError("File metadata missing keys: %s. Got %s", missing, meta)
    
    return meta

def _build_file_path(meta: Dict[str, Any]) -> Path:
    """Resolve the actual file path inside DATA_DIR."""
    rel_path = meta["path"]
    path = DATA_DIR / rel_path
    if not path.exists():
        log.error("Data file not found: %s.", path)
        raise FileNotFoundError(f"Data file not found: {path}")
    return path

def _produce_row(
        producer,
        meta: Dict[str, Any],
        row: Dict[str, object],
        row_index: int,
) -> None:
    """
    Produce a single OHLCV row to ROWS_TOPIC.

    Includes: 
      - file_id (to link back to source file)
      - row_index
      - symbol, trade_date, ohlcv
    """
    payload: Dict[str, Any] = {
        "file_id": meta["file_id"],
        "row_index": row_index,
        **row, # symbol, trade_date, open, high, low, close, volume
    }

    key = f"{meta['file_id']}:{row['symbol']}:{row['trade_date']}"

    producer.produce(
        ROWS_TOPIC,
        key=key.encode("utf-8"),
        value=json.dumps(payload).encode("utf-8"),
        on_delivery=_delivery_report,
    )

def _delivery_report(err, msg: Message):
    """Kafka delivery callback for produced row messages."""
    if err is not None:
        log.error(
            "Failed to deliver row message to %s: %s",
            msg.topic(),
            err,
        )
    else:
        log.debug(
            "Row message delivered to %s[%s] at offset %s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )
    
def process_file_message(producer, msg: Message) -> None:
    """
    Handle a single message from files_to_process:

        1. Parse metadata
        2. Resolve file path
        3. Iterate rows via iter_ohclv_rows
        4. Produce per-row messages to rows_to_process
    """
    meta = _parse_file_metadata(msg)
    file_id = meta["file_id"]

    log.info("Processing file_id=%s metadata: %s", file_id, meta)

    path = _build_file_path(meta)

    # Prefer symbol from metadata; fall back to derive_symbol()
    symbol_hint = meta.get("symbol_hint")

    row_count = 0
    for i, row in enumerate(iter_ohlcv_rows(path, symbol_hint=symbol_hint)):
        try:
            _produce_row(producer, meta, row, row_index=i)
            row_count += 1
        except Exception:
            log.error(
                "Failed to produce row %s for file_id=%s (%s)",
                i,
                file_id,
                path,
                exc_info=True,
            )
            continue
    
    log.info(
        "Finished atomizing file_id=%s (%s). Emitted %s rows.",
        file_id,
        path.name,
        row_count,
    )
    producer.flush()

def _graceful_shutdown(consumer):
    log.info("Shutting down row_atomizer consumer...")
    try:
        consumer.close()
    except Exception:
        log.info("Error while closing consumer.")
    log.info("Shutdown complete.")

def main() -> None:
    log.info("Starting row_atomizer. Subscribing to topic: %s", FILES_TOPIC)

    consumer = create_consumer(group_id=GROUP_ID, client_id="row_atomizer")
    producer = create_producer(client_id="row_atomizer")

    running = True

    def handle_signal(signum, frame):
        nonlocal running
        log.info("Received signal %s, requesting shutdown...", signum)
        running = False

    # Handle Ctrl+C / docker stop
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    consumer.subscribe([FILES_TOPIC])

    try:
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                log.error("Consumer error %s", msg.error())
                continue

            try: 
                process_file_message(producer, msg)
                # Explicit commmit for exactly-once-ish semantics
                consumer.commit(msg)
            except FileNotFoundError as e:
                log.error("File not found for message: %s", e, exc_info=True)
                # Send to DLQ for later (make dlq helper function in a new feat)

                # dlq = create_producer("row_dlq")
            except Exception:
                log.error(
                    "Unexpected error processing message from %s",
                    FILES_TOPIC,
                    exc_info=True,
                )
    finally:
        _graceful_shutdown(consumer)

if __name__=="__main__":
    main()

    
        





