import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR =  Path("/app/logs")
LOG_DIR.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Format logs
    formatter = logging.Formatter(
        "%(asctime)s [%(name)s] [%(levelname)s] %(messages)s"
    )

    # Rotating file handler (5 MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=5_000_000,
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    # Also log to stdout (so Docker logs see it)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.propagate = False
    return logger