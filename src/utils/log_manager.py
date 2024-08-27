from os import getenv
from sys import stderr

from loguru import logger


def setup_logger() -> None:
    # Get log level from environment variable, default to INFO
    log_level = getenv("LOG_LEVEL", "DEBUG").upper()

    # Configure logger
    logger.remove()  # Remove default handler
    logger.add(sink=stderr, level=log_level)
