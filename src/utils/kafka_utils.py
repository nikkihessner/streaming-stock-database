from confluent_kafka import Producer, Consumer
from stock_pipeline.config import get_kafka_bootstrap_servers
from utils.logging_config  import get_logger

log = get_logger("kafka_utils")

def create_producer(client_id: str) -> Producer:
    bootstrap_servers = get_kafka_bootstrap_servers()

    conf = {
        "bootstrap.servers": bootstrap_servers,
        "client.id": client_id,
        "enable.idempotence": True,
    }

    log.info("Creating Kafka producer with client_id=%s", client_id)
    return Producer(conf)

def create_consumer(group_id: str, client_id: str) -> Consumer:
    bootstrap_servers = get_kafka_bootstrap_servers()

    conf = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "client.id": client_id,

        # Defaults
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }

    log.info("Creating Kafka consumer with group_id=%s client_id=%s", group_id, client_id)
    return Consumer(conf)