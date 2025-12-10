from stock_analysis.config import get_config
import os

def test_config_defaults(monkeypatch):
    # clear env vars
    for key in [
        "KAFKA_BROKERS",
        "KAFKA_TOPIC_ANALYSIS_JOBS",
        "KAFKA_TOPIC_SYMBOL_SLICES",
        "KAFKA_TOPIC_ANALYSIS_RESULTS",
        "KAFKA_CONSUMER_GROUP",
        "REDIS_URL",
        "REDIS_SYMBOL_PREFIX",
        "REDIS_DONE_PREFIX",
        "ANALYSIS_DEFAULT_TIMEFRAME",
        "ANALYSIS_ENABLED_PATTERNS",
    ]:
        monkeypatch.delenv(key, raising=False)
    
    get_config.cache_clear() # type: ignore

    cfg = get_config()

    assert cfg.kafka.brokers == "localhost:9092"
    assert cfg.kafka.analysis_jobs_topic == "analysis_jobs"
    assert cfg.redis.url == "redis://localhost:6379/0"
    assert cfg.analysis.default_timeframe == "1D"
    assert "IMPULSE" in cfg.analysis.enabled_patterns

def test_config_overrides(monkeypatch):
    monkeypatch.setenv("KAFKA_BROKERS", "kafka:9092")
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/1")
    monkeypatch.setenv("ANALYSIS_DEFAULT_TIMEFRAME", "4H")
    monkeypatch.setenv("ANALYSIS_ENABLED_PATTERNS", "impulse,regular_flat")

    get_config.cache_clear()

    cfg = get_config()

    assert cfg.kafka.brokers == "kafka:9092"
    assert cfg.redis.url == "redis://redis:6379/1"
    assert cfg.analysis.default_timeframe == "4H"
    assert cfg.analysis.enabled_patterns == ("IMPULSE", "REGULAR_FLAT")