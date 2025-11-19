import os
from enum import Enum

from utils.logging_config import get_logger

log = get_logger("config")

class AppEnv(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

def get_app_env() -> AppEnv:
    raw = os.environ.get("APP_ENV", "local").lower()
    try:
        return AppEnv(raw)
    except ValueError:
        log.error(f"Invalid App_ENV={raw!r}. Expected one of {[e.value for e in AppEnv]}")
        raise RuntimeError(f"Invalid APP_ENV{raw!r}. Expected one of: {[e.value for e in AppEnv]}")

def get_kafka_bootstrap_servers() -> str:
    env =  get_app_env()
    value = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")

    if value:
        return value
    
    if env is AppEnv.LOCAL:
        # Only allowed in local dev
        default = "kafka:9092"
        log.warning(
            "KAFKA_BOOTSTRAP_SERVERS not set; using local default %s (APP_ENV=%s)",
            default,
            env.value,
        )
        return default
    
    # In non-local envs. fail hard if misconfigured
    log.error(
        "KAFKA_BOOTSTRAP_SERVERS is missing but required when APP_ENV=%s",
        env.value,
    )
    raise RuntimeError(
        f"KAFKA_BOOTSTRAP_SERVERS must be set when APP_ENV={env.value}.\nRefusing to fall back to a default."
    )