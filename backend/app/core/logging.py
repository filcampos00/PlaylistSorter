"""Centralized logging configuration."""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Define log directory relative to the project root (assuming this file is in backend/app/core/)
# We want logs to be in <project_root>/logs
LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "playlist_sorter.log"


def setup_logging():
    """Configure application-wide logging."""
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Check if logging is already configured (singleton pattern)
    logger = logging.getLogger()
    if logger.hasHandlers():
        return

    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File Handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Ensure no handlers are duplicated if setup is called multiple times
    # (though in main.py it acts as a script entry point usually)

    # Explicitly remove StreamHandler if present (to adhere to user request of NO console logs)
    # However, by default, the root logger might not have one unless added.
    # If UVICORN adds one, we might want to leave it for Uvicorn's own logs,
    # but for OUR app logs, we just won't add a StreamHandler.

    # If we really want to silence console for our app, we don't add StreamHandler.
    # Note: Uvicorn has its own logging config.

    # Silence noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info("Logging initialized. Writing to %s", LOG_FILE)
