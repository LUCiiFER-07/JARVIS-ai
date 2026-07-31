"""
Central logging configuration for JARVIS AI.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ---------------------------------------------------------------------
# Log configuration
# ---------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "jarvis.log"

LOG_LEVEL = logging.INFO

LOG_FORMAT = (
    "%(levelname)-8s |"
    "%(name)s |"
    "%(message)s"
)

# ---------------------------------------------------------------------
# Configure root logger
# ---------------------------------------------------------------------

_root_logger = logging.getLogger()

if not _root_logger.handlers:

    _root_logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    _root_logger.addHandler(file_handler)
    _root_logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Args:
        name: Name of the module.

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)