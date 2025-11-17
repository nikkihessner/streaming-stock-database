# src/file_watcher.py
import json
import os
from pathlib import Path

from confluent_kafka import Producer

from stock_pipeline.utils.file_utils import list_xlsx_files, build_file_metadata

DATA_DIR = Path("/app/data")
TOPIC = "files_to_process"

def create_producer() -> Producer:
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    conf = {
        "bootstrap.servers": bootstrap_servers,
        "client.id": "file-watcher",
        "enable.idempotence": True
    }
    return Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Deliver failed for record {msg.key()}: {err}")
    else:
        print(f"Record sent to {msg.topic()}[{msg.partition()}] at offset {msg.offset()}")

def main() -> None:
    files = list_xlsx_files(DATA_DIR)
    if not files:
        print("No .xlsx files found in ", DATA_DIR)
        return
    
    producer = create_producer()

    for f in files:
        meta = build_file_metadata(f)
        key = meta["file_id"]
        value = json.dumps(meta)

        print(f"Producing for file {f.name}: {meta}")
        producer.produce(
            TOPIC,
            key=key.encode("utf-8"),
            value=value.encode("utf-8"),
            callback=delivery_report,
        )

        # Make sure everything is sent before exiting
        print("Flushing producer...")
        producer.flush()

if __name__ == "__main__":
    main()