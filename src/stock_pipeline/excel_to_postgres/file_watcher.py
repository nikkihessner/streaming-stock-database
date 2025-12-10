# src/stock_pipeline/file_watcher.py
import json
import os
from pathlib import Path
from utils.logging_config import get_logger
from stock_pipeline.config import TOPICS, DATA_DIR, get_kafka_bootstrap_servers, get_app_env
from utils.kafka_utils import create_producer
from stock_pipeline.utils.file_utils import list_xlsx_files, build_file_metadata

log = get_logger("file_watcher")

TOPIC = TOPICS.FILES_TO_PROCESS

def delivery_report(err, msg):
    if err is not None:
        log.error(f"Deliver failed for record {msg.key()}: {err}")
    else:
        log.info(f"Record sent to {msg.topic()}[{msg.partition()}] at offset {msg.offset()}")

def main() -> None:
    files = list_xlsx_files(DATA_DIR)
    if not files:
        log.info("No .xlsx files found in ", DATA_DIR)
        return
    
    producer = create_producer("file-watcher")

    for f in files:
        meta = build_file_metadata(f)
        key = meta["file_id"]
        value = json.dumps(meta)

        log.info(f"Producing metadata for file {f.name}: {meta}")
        producer.produce(
            TOPIC,
            key=key.encode("utf-8"),
            value=value.encode("utf-8"),
            callback=delivery_report,
        )

        # Make sure everything is sent before exiting
        log.debug("Flushing Kafka producer buffer")
        producer.flush()

if __name__ == "__main__":
    main()