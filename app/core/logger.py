"""Centralised logging configuration.

Call ``setup_logging()`` exactly once at application startup (in ``main.py``)
before any other module emits log records.  Every other module should obtain
its own logger via ``logging.getLogger(__name__)`` — no further configuration
is needed in those files.

Log level precedence (lowest → highest):
    DEBUG → INFO → WARNING → ERROR → CRITICAL

The active level is controlled by the ``LOG_LEVEL`` environment variable
(default: ``INFO``).  Set it to ``DEBUG`` during local development for
verbose output, and ``WARNING`` or higher in production to reduce noise.
"""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """Configure the root logger for the entire application.

    Sets a consistent format on a single ``StreamHandler`` writing to stdout.
    Calling this function more than once is safe — subsequent calls are
    no-ops because the root logger's handlers are only added when empty.

    Args:
        log_level: Case-insensitive log level string (e.g. ``"INFO"``,
            ``"DEBUG"``, ``"WARNING"``).  Invalid values fall back to
            ``INFO`` with a warning.
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        # Fallback gracefully rather than crashing at startup.
        numeric_level = logging.INFO
        logging.warning("Invalid LOG_LEVEL=%r; defaulting to INFO.", log_level)

    root_logger = logging.getLogger()

    # Avoid adding duplicate handlers if setup_logging is called again
    # (e.g. during testing with multiple TestClient instantiations).
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger.setLevel(numeric_level)
    root_logger.addHandler(handler)
