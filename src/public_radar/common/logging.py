"""Logging configuration for Public Radar.

This module provides structured logging setup for the application.
"""

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
    level: LogLevel | int = "INFO",
    format_string: str | None = None,
) -> None:
    """Configure logging for the application.

    Sets up a consistent logging format with timestamps and module names.

    :param level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) or int.
    :type level: LogLevel | int
    :param format_string: Custom format string.
    :type format_string: str | None

    Example::

        setup_logging(level="DEBUG")
        logger = logging.getLogger(__name__)
        logger.info("Application started")
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Convert string level to int if needed
    if isinstance(level, str):
        level_int = getattr(logging, level)
    else:
        level_int = level

    logging.basicConfig(
        level=level_int,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("tenacity").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Convenience function for getting a logger.

    :param name: Logger name (typically __name__).
    :type name: str
    :return: Logger instance.
    :rtype: logging.Logger

    Example::

        logger = get_logger(__name__)
        logger.info("Processing started")
    """
    return logging.getLogger(name)
