"""Configuration for separate KINSURE operation and error log files."""

import logging
from pathlib import Path

from .config import settings


def configure_logging() -> None:
    """Create file handlers for ordinary operations and application errors."""
    log_directory = Path(settings.log_directory)
    log_directory.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    for logger_name, filename, level in (
        ("kinsure.operations", "operations.log", logging.INFO),
        ("kinsure.errors", "errors.log", logging.ERROR),
    ):
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = False
        if not logger.handlers:
            handler = logging.FileHandler(
                log_directory / filename,
                encoding="utf-8",
            )
            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)


def log_operation(action: str, resource: str, actor: str) -> None:
    """Write a successful data change without recording sensitive field values."""
    logging.getLogger("kinsure.operations").info(
        "işlem=%s kaynak=%s kullanıcı=%s",
        action,
        resource,
        actor,
    )
