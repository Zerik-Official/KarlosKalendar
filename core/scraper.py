"""
Agenda scraper for the UNAD calendar pages.

Fetches the agenda HTML through the authenticated session, parses it
into structured data, stores it as JSON under calendars/ and detects
changes between consecutive scrapes.
"""

# Standard library
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Final, List, Tuple

# Third-party
from bs4 import BeautifulSoup, Tag

# Project imports
from core.client import CampusClient
from schemas.schemas import AgendaActivity, AgendaSection, CalendarAgenda
from utils.constants import REQUEST_TIMEOUT
from utils.log import log, Tags

CALENDARS_DIR: Final[Path] = Path(__file__).resolve().parent.parent / "calendars"
AGENDA_URL_PATTERN: Final[str] = r"^https?://.+/[0-9]+\.htm$"
ACTIVITY_COLUMNS: Final[int] = 10


def extract_agenda_code(url: str) -> str | None:
    """
    Extract the numeric agenda code from an agenda URL.

    Args:
        url (str): Agenda page URL.

    Returns:
        str | None: The agenda code, or None if the URL is not a valid agenda.
    """
    match = re.search(r"/([0-9]+)\.htm$", url)
    return match.group(1) if match else None


def fetch_agenda(client: CampusClient, url: str) -> str | None:
    """
    Fetch the agenda page HTML through the authenticated session.

    Args:
        client (CampusClient): Authenticated client.
        url (str): Agenda page URL.

    Returns:
        str | None: The raw HTML, or None if the request failed.
    """
    response = client.session.get(url, timeout=REQUEST_TIMEOUT)
    if response.status_code != 200:
        log(
            "ERROR",
            Tags.SCRAPER,
            f"Failed to fetch {url}, status: {response.status_code}",
        )
        return None
    log("INFO", Tags.SCRAPER, f"Fetched {url}, bytes: {len(response.text)}")
    return response.text


def parse_agenda(html: str, code: str) -> CalendarAgenda:
    """
    Parse an agenda page HTML into structured agenda data.

    Args:
        html (str): Raw HTML of the agenda page.
        code (str): Agenda code (stored as identifier).

    Returns:
        CalendarAgenda: Parsed agenda with sections and activities.

    Raises:
        ValueError: If the agenda header elements are missing.
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    name, credits, period = _parse_header(soup, code)

    sections: List[AgendaSection] = []
    current_title: str = ""
    current_activities: List[AgendaActivity] = []
    pending_rowspans: Dict[int, List[Any]] = {}

    for row in soup.select("table tr"):
        section_header: Tag | None = _find_section_header(row)
        if section_header is not None:
            _flush_section(sections, current_title, current_activities)
            current_title = section_header.get_text(strip=True)
            current_activities = []
            pending_rowspans = {}
            continue

        cells: List[Tag] = row.find_all("td", recursive=False)
        if not cells:
            continue

        values: List[str] = _row_values(cells, pending_rowspans)
        current_activities.append(_to_activity(values))

    _flush_section(sections, current_title, current_activities)

    return CalendarAgenda(
        code=code,
        name=name,
        credits=credits,
        period=period,
        sections=sections,
    )


def save_agenda(agenda: CalendarAgenda) -> Path:
    """
    Store the agenda data as JSON under calendars/.

    Args:
        agenda (CalendarAgenda): Parsed agenda to persist.

    Returns:
        Path: Path of the written JSON file.
    """
    CALENDARS_DIR.mkdir(parents=True, exist_ok=True)
    path: Path = CALENDARS_DIR / f"{agenda.code}.json"
    data: dict = asdict(agenda)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_agenda_data(code: str) -> dict | None:
    """
    Load the stored JSON data of an agenda.

    Args:
        code (str): Agenda code.

    Returns:
        dict | None: The stored agenda data, or None if not saved yet.
    """
    path: Path = CALENDARS_DIR / f"{code}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def scrape_and_update(client: CampusClient, url: str) -> None:
    """
    Scrape an agenda, compare it with the stored JSON and update it if changed.

    Args:
        client (CampusClient): Authenticated client.
        url (str): Agenda page URL.

    Returns:
        None
    """
    code: str | None = extract_agenda_code(url)
    if code is None:
        log("ERROR", Tags.SCRAPER, f"Invalid agenda URL: {url}")
        return

    html: str | None = fetch_agenda(client, url)
    if html is None:
        return

    try:
        agenda: CalendarAgenda = parse_agenda(html, code)
    except ValueError as exc:
        log("ERROR", Tags.SCRAPER, f"Failed to parse {url}: {exc}")
        return

    new_data: dict = asdict(agenda)
    saved_data: dict | None = load_agenda_data(code)
    if saved_data == new_data:
        log("INFO", Tags.SCRAPER, f"Agenda {code}: no changes")
        return

    save_agenda(agenda)
    if saved_data is None:
        log("SUCCESS", Tags.SCRAPER, f"Agenda {code} saved for the first time")
    else:
        log("SUCCESS", Tags.SCRAPER, f"Agenda {code} updated")


def _parse_header(
    soup: BeautifulSoup, code: str
) -> Tuple[str, str, str]:
    """
    Extract the agenda name, credits and period from the page header.

    Args:
        soup (BeautifulSoup): Parsed HTML document.
        code (str): Agenda code (used as fallback).

    Returns:
        tuple: (name, credits, period).
    """
    name: str = ""
    credits: str = ""
    period: str = ""

    name_paragraphs: List[Tag] = soup.select("div.agenda__nombre p")
    if name_paragraphs:
        name, credits = _split_name_credits(name_paragraphs[0].get_text(strip=True))
        if len(name_paragraphs) > 1:
            period = name_paragraphs[1].get_text(strip=True)

    if not name:
        title: Tag | None = soup.select_one("title")
        if title is not None:
            name = title.get_text(strip=True)
            name = name.replace("Agenda - ", "").replace(f"{code} - ", "")

    if not name and not period:
        raise ValueError("Agenda header elements not found in the page.")

    return name, credits, period


def _split_name_credits(text: str) -> Tuple[str, str]:
    """
    Split the header text into course name and credits part.

    Args:
        text (str): Full header text.

    Returns:
        tuple: (name, credits).
    """
    match = re.search(r"\s+\([^)]+\)\s*-\s*[0-9]+\s+de\s+[0-9]+\s+cr[ée]ditos?$", text)
    if match is None:
        return text, ""
    return text[: match.start()].strip(), match.group(0).strip()


def _find_section_header(row: Tag) -> Tag | None:
    """
    Find the section header (th with colspan) of a table row.

    Args:
        row (Tag): Table row element.

    Returns:
        Tag | None: The section header th, or None if the row is not a header.
    """
    for header in row.find_all("th", recursive=False):
        if header.get("colspan"):
            return header
    return None


def _row_values(cells: List[Tag], pending: Dict[int, List[Any]]) -> List[str]:
    """
    Collect the cell values of a row, propagating rowspan values.

    Args:
        cells (list): td elements of the row.
        pending (dict): Rowspan values pending from previous rows.

    Returns:
        list: The cell values of the row.
    """
    values: List[str] = []
    column: int = 0
    cell_index: int = 0

    while cell_index < len(cells) or column in pending:
        if column in pending:
            value, remaining = pending[column]
            values.append(value)
            remaining -= 1
            if remaining <= 0:
                del pending[column]
            else:
                pending[column][1] = remaining
        else:
            cell: Tag = cells[cell_index]
            cell_index += 1
            value: str = cell.get_text(" ", strip=True)
            values.append(value)
            rowspan: str | None = cell.get("rowspan")
            if rowspan is not None and rowspan.isdigit() and int(rowspan) > 1:
                pending[column] = [value, int(rowspan) - 1]
        column += 1

    return values


def _to_activity(values: List[str]) -> AgendaActivity:
    """
    Build an AgendaActivity from the row values.

    Args:
        values (list): Cell values of the row.

    Returns:
        AgendaActivity: The activity built from the values.
    """
    padded: List[str] = (values + [""] * ACTIVITY_COLUMNS)[:ACTIVITY_COLUMNS]
    return AgendaActivity(
        moment=padded[0],
        rac=padded[1],
        name=padded[2],
        description=padded[3],
        activity_type=padded[4],
        weight=padded[5],
        start=padded[6],
        end=padded[7],
        alert=padded[8],
        feedback=padded[9],
    )


def _flush_section(
    sections: List[AgendaSection],
    title: str,
    activities: List[AgendaActivity],
) -> None:
    """
    Append the current section to the sections list.

    Args:
        sections (list): Accumulated sections.
        title (str): Title of the current section.
        activities (list): Activities of the current section.

    Returns:
        None
    """
    if title:
        sections.append(AgendaSection(title=title, activities=activities))
