from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.core.config import settings

SERVICE_NAME = settings.service_name


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "service": SERVICE_NAME,
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for field_name in ("correlation_id", "job_id", "repo_id", "request_id"):
            value = getattr(record, field_name, None)
            if value is not None:
                payload[field_name] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = SERVICE_NAME, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


logger = get_logger()


def with_context(**extra: object) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, extra)
