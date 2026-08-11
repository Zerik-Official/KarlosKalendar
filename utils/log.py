"""
Custom logger with support for tags and log levels.

Allows filtering by tags and levels, and is safe for use across
multiple threads.
"""

# Standard library
import threading
from enum import StrEnum, unique
from typing import Final, Set, Dict
from datetime import datetime

# Third-party
from colorama import Fore, Style

# Project imports
from schemas.schemas import LogLevel


# Global lock for the logger to avoid concurrency issues.
_log_lock: threading.Lock = threading.Lock()

# If not empty, only these tags are shown. Empty = show all.
ENABLED_TAGS: Final[Set[str]] = set()

# Levels ignored globally for all tags.
DISABLED_LEVELS: Final[Set[str]] = set()

# Per-tag rules: levels to IGNORE for a specific tag.
# Example: "LOADER": {"DEBUG"} -> silences DEBUG only for LOADER
TAG_LEVEL_RULES: Dict[str, Set[str]] = {}


@unique
class Tags(StrEnum):
    MAIN = "MAIN"
    CLIENT = "CLIENT"
    PARSER = "PARSER"
    LOGIN = "LOGIN"


def log(level: LogLevel, tag: Tags | str, message: str) -> None:
    """
    Print a log message with filtering by tag and level.

    Args:
        level (str): Log level (INFO, SUCCESS, WARNING, ERROR, DEBUG, CRITICAL).
        tag (str): Module tag (e.g. MAIN, CORE, Browser).
        message (str): Message to print to the console.

    Returns:
        None
    """
    level_up: str = level.upper()
    tag_up: str = tag.upper()

    if level_up in DISABLED_LEVELS:
        return

    if ENABLED_TAGS and tag_up not in ENABLED_TAGS:
        return

    if tag_up in TAG_LEVEL_RULES and level_up in TAG_LEVEL_RULES[tag_up]:
        return

    timestamp: str = datetime.now().strftime("%H:%M:%S")

    colors: Final[Dict[str, str]] = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.MAGENTA,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    color: str = colors.get(level_up, Fore.WHITE)

    lvl_fmt: str = f"{level_up:^9}"
    tag_fmt: str = f"{tag_up:^20}"

    with _log_lock:
        print(
            f"{Style.DIM}{timestamp}{Style.RESET_ALL} "
            f"[{color}{lvl_fmt}{Style.RESET_ALL}] "
            f"[{Fore.WHITE}{Style.BRIGHT}{tag_fmt}{Style.RESET_ALL}] "
            f"{message}"
        )