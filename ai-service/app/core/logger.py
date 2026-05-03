from __future__ import annotations
import logging
import sys
import json
from typing import Optional, Dict

SERVICE_NAME = "ai-service"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Optional[str]] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "service": SERVICE_NAME,
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        # include extra fields if present on the LogRecord
        if getattr(record, "correlation_id", None):
            log_record["correlation_id"] = record.correlation_id
        if getattr(record, "job_id", None):
            log_record["job_id"] = record.job_id
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


def get_logger(name: str = SERVICE_NAME, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    # avoid adding multiple handlers when module is imported multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


# module-level logger for convenience
logger = get_logger()


def with_context(**extra: object) -> logging.LoggerAdapter:
    """Return a LoggerAdapter that injects `extra` into log records.

    Usage:
        log = with_context(correlation_id='abc123', job_id='job-1')
        log.info('started')
    """
    return logging.LoggerAdapter(logger, extra)
