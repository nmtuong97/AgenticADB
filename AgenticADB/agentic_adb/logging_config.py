import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configures production-grade logging with rotation for AgenticADB."""
    log_level_str = os.environ.get("AGENTIC_ADB_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    log_file = os.environ.get("AGENTIC_ADB_LOG_FILE", "agentic_adb.log")
    log_console = os.environ.get("AGENTIC_ADB_LOG_CONSOLE", "0") == "1"

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handlers = []

    # Rotating file handler: 10MB per file, 5 backups
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    # Optional console handler
    if log_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # Configure root logger
    logging.basicConfig(level=log_level, handlers=handlers, force=True)

    # Ensure root logger's level is explicitly set in case basicConfig ignores it due to earlier configurations
    logging.getLogger().setLevel(log_level)
