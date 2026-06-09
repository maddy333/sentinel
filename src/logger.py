import logging
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log messages in a structured JSON format.
    Useful for log aggregators like ELK, Fluentd, or Datadog.
    """
    def __init__(self, service_name: str = "sentinel-ai"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
        }

        # Include exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include extra attributes if passed
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            for key, val in record.extra.items():
                log_data[key] = val

        # Add trace or context keys if available in record.__dict__
        for key in ["trace_id", "agent_name", "workflow_id", "status"]:
            if key in record.__dict__:
                log_data[key] = record.__dict__[key]

        return json.dumps(log_data)

def setup_logger(name: str = "sentinel-ai", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JSONFormatter(service_name=name)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
