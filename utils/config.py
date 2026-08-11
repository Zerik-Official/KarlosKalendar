"""
Configuration manager.

Loads and saves the application configuration (config/config.json)
with the scrape interval and the registered calendar URLs.
"""

# Standard library
import json
from dataclasses import replace
from pathlib import Path
from typing import Final, List

# Project imports
from schemas.schemas import AppConfig

CONFIG_DIR: Final[Path] = Path(__file__).resolve().parent.parent / "config"
CONFIG_PATH: Final[Path] = CONFIG_DIR / "config.json"
DEFAULT_INTERVAL_MINUTES: Final[int] = 5


def load_config() -> AppConfig:
    """
    Load the configuration from disk, creating a default one if missing.

    Returns:
        AppConfig: The loaded (or default) configuration.
    """
    if not CONFIG_PATH.exists():
        default: AppConfig = AppConfig(
            interval_minutes=DEFAULT_INTERVAL_MINUTES,
            calendars=[],
        )
        save_config(default)
        return default

    data: dict = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return AppConfig(
        interval_minutes=int(data.get("interval_minutes", DEFAULT_INTERVAL_MINUTES)),
        calendars=[str(url) for url in data.get("calendars", [])],
    )


def save_config(config: AppConfig) -> None:
    """
    Write the configuration to disk as JSON.

    Args:
        config (AppConfig): Configuration to persist.

    Returns:
        None
    """
    data: dict = {
        "interval_minutes": config.interval_minutes,
        "calendars": config.calendars,
    }
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def add_calendar(config: AppConfig, url: str) -> AppConfig:
    """
    Return a copy of the config with a calendar URL added.

    Args:
        config (AppConfig): Current configuration.
        url (str): Agenda URL to register.

    Returns:
        AppConfig: Updated configuration.
    """
    if url in config.calendars:
        return config
    return replace(config, calendars=config.calendars + [url])


def remove_calendars(config: AppConfig, urls: List[str]) -> AppConfig:
    """
    Return a copy of the config with the given calendar URLs removed.

    Args:
        config (AppConfig): Current configuration.
        urls (list): Agenda URLs to remove.

    Returns:
        AppConfig: Updated configuration.
    """
    return replace(config, calendars=[url for url in config.calendars if url not in urls])


def set_interval(config: AppConfig, interval_minutes: int) -> AppConfig:
    """
    Return a copy of the config with the scrape interval changed.

    Args:
        config (AppConfig): Current configuration.
        interval_minutes (int): New interval in minutes.

    Returns:
        AppConfig: Updated configuration.
    """
    return replace(config, interval_minutes=interval_minutes)
