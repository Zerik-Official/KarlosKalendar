# Standard library
import argparse
import time

# Third-party
from colorama import init
from dotenv import load_dotenv

# Project imports
from core.client import CampusClient, create_authenticated_client
from core.parser import parse_user_profile
from core.scraper import scrape_and_update
from schemas.schemas import AppConfig, UserProfile
from utils.config import load_config
from utils.config_menu import run_config_menu
from utils.display import print_profile
from utils.log import log, Tags
from utils.banner import BANNER

init(autoreset=True)

# Load the credentials from the .env file.
load_dotenv()


def main() -> None:
    """
    Entry point of the application.

    Without arguments it authenticates and runs the scrape scheduler.
    With --config it opens the interactive configuration menu.

    Returns:
        None
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="KarlosKalendar CLI"
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Open the interactive configuration menu",
    )
    args: argparse.Namespace = parser.parse_args()

    if args.config:
        run_config_menu()
        return

    run_scheduler()


def run_scheduler() -> None:
    """
    Run the periodic scraping loop.

    Scrapes all registered calendars, compares them with the stored
    JSON files and updates them when the data changed. Repeats every
    configured interval.

    Returns:
        None
    """
    config: AppConfig = load_config()
    if not config.calendars:
        log(
            "WARNING",
            Tags.MAIN,
            "No calendars registered, run with --config to add one",
        )
        return

    log("INFO", Tags.MAIN, "Starting KarlosKalendar...")

    client: CampusClient = create_authenticated_client()
    if client.user_id is None:
        log("ERROR", Tags.MAIN, "Authentication failed, check the .env credentials")
        return

    html: str = client.fetch_profile_page()
    profile: UserProfile = parse_user_profile(html)
    log(
        "SUCCESS",
        Tags.MAIN,
        f"Profile of {profile.full_name} (id {profile.user_id})",
    )
    print_profile(profile)

    interval_seconds: int = config.interval_minutes * 60
    log(
        "INFO",
        Tags.MAIN,
        f"Scraping {len(config.calendars)} calendar(s) every "
        f"{config.interval_minutes} minute(s)",
    )

    try:
        while True:
            _scrape_all(client, config)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        log("INFO", Tags.MAIN, "Stopped by user")


def _scrape_all(client: CampusClient, config: AppConfig) -> None:
    """
    Scrape all registered calendars and update the stored data if changed.

    Args:
        client (CampusClient): Authenticated client.
        config (AppConfig): Current configuration.

    Returns:
        None
    """
    for url in config.calendars:
        scrape_and_update(client, url)


if __name__ == "__main__":
    print(BANNER)
    main()
