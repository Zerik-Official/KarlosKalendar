"""
Interactive configuration menu.

Uses InquirerPy to manage the registered calendars and the scrape
interval (--config mode of the CLI).
"""

# Standard library
import re
from typing import Final, List

# Third-party
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table

# Project imports
from core.client import CampusClient, create_authenticated_client
from core.scraper import AGENDA_URL_PATTERN, scrape_and_update
from schemas.schemas import AppConfig
from utils.config import (
    add_calendar,
    load_config,
    remove_calendars,
    save_config,
    set_interval,
)
from utils.log import log, Tags

_CONSOLE: Final[Console] = Console()

_ADD: Final[str] = "add"
_REMOVE: Final[str] = "remove"
_LIST: Final[str] = "list"
_INTERVAL: Final[str] = "interval"
_EXIT: Final[str] = "exit"


def run_config_menu() -> None:
    """
    Run the interactive configuration menu.

    Allows adding, removing and listing calendars, changing the scrape
    interval and scraping a newly added calendar immediately.

    Returns:
        None
    """
    config: AppConfig = load_config()

    while True:
        action: str = inquirer.select(
            message="Select an option",
            choices=[
                {"name": "Add calendar", "value": _ADD},
                {"name": "Remove calendars", "value": _REMOVE},
                {"name": "List calendars", "value": _LIST},
                {"name": "Set scrape interval", "value": _INTERVAL},
                {"name": "Exit", "value": _EXIT},
            ],
        ).execute()

        if action == _ADD:
            config = _add_calendar_flow(config)

        elif action == _REMOVE:
            config = _remove_calendars_flow(config)

        elif action == _LIST:
            _list_calendars(config)

        elif action == _INTERVAL:
            config = _set_interval_flow(config)

        else:
            save_config(config)
            log("INFO", Tags.CONFIG, "Configuration saved")
            return


def _add_calendar_flow(config: AppConfig) -> AppConfig:
    """
    Prompt for a new agenda URL, register it and offer to scrape it now.

    Args:
        config (AppConfig): Current configuration.

    Returns:
        AppConfig: Updated configuration.
    """
    url: str = inquirer.text(
        message="Enter the agenda URL",
        validate=lambda value: re.match(AGENDA_URL_PATTERN, value) is not None,
        invalid_message=(
            "The URL must be an agenda page, e.g. "
            "https://datateca.unad.edu.co/contenidos/agendas/2026-2204/212014.htm"
        ),
    ).execute()

    config = add_calendar(config, url)
    save_config(config)
    log("INFO", Tags.CONFIG, f"Calendar added: {url}")

    if inquirer.confirm(message="Scrape it now?").execute():
        _scrape_now(url)

    return config


def _remove_calendars_flow(config: AppConfig) -> AppConfig:
    """
    Prompt for the calendars to remove and unregister them.

    Args:
        config (AppConfig): Current configuration.

    Returns:
        AppConfig: Updated configuration.
    """
    if not config.calendars:
        log("WARNING", Tags.CONFIG, "No calendars registered")
        return config

    selected: List[str] = inquirer.checkbox(
        message="Select calendars to remove",
        choices=config.calendars,
    ).execute()

    if selected:
        config = remove_calendars(config, selected)
        save_config(config)
        log("INFO", Tags.CONFIG, f"Removed {len(selected)} calendar(s)")

    return config


def _list_calendars(config: AppConfig) -> None:
    """
    Print the registered calendars as a table.

    Args:
        config (AppConfig): Current configuration.

    Returns:
        None
    """
    if not config.calendars:
        log("INFO", Tags.CONFIG, "No calendars registered")
        return

    table: Table = Table(title="Registered calendars")
    table.add_column("URL", style="cyan")
    for url in config.calendars:
        table.add_row(url)
    _CONSOLE.print(table)


def _set_interval_flow(config: AppConfig) -> AppConfig:
    """
    Prompt for the scrape interval in minutes.

    Args:
        config (AppConfig): Current configuration.

    Returns:
        AppConfig: Updated configuration.
    """
    interval: str = inquirer.number(
        message="Scrape interval in minutes",
        default=str(config.interval_minutes),
        min_allowed=1,
        invalid_message="The interval must be a positive number",
    ).execute()

    config = set_interval(config, int(interval))
    save_config(config)
    log("INFO", Tags.CONFIG, f"Interval set to {int(interval)} minute(s)")

    return config


def _scrape_now(url: str) -> None:
    """
    Scrape a single agenda immediately with a fresh authenticated client.

    Args:
        url (str): Agenda page URL.

    Returns:
        None
    """
    client: CampusClient = create_authenticated_client()
    if client.user_id is None:
        log("ERROR", Tags.CONFIG, "Authentication failed, cannot scrape")
        return
    scrape_and_update(client, url)
