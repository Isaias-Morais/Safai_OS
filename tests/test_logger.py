import logging
import json
from src.utils.logger import setup_logger, JsonFormatter

def test_setup_logger():
    logger = setup_logger("test_safai", level=logging.DEBUG)
    assert logger.name == "test_safai"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1

def test_json_formatter():
    formatter = JsonFormatter()
    record = logging.LogRecord("test", logging.INFO, "test.py", 10, "Hello JSON", (), None)
    out = formatter.format(record)
    data = json.loads(out)
    assert data["message"] == "Hello JSON"
    assert data["level"] == "INFO"
    assert "timestamp" in data
