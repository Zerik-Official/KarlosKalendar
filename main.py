# Standard library
import os
from typing import Final, List, Tuple

# Third-party
from colorama import init
from dotenv import load_dotenv

# Project imports
from core.client import CampusClient
from core.parser import parse_user_profile
from schemas.schemas import UserProfile
from utils.log import log, Tags

init(autoreset=True)

# Load the credentials from the .env file.
load_dotenv()

# Document type used for the portal login.
DOCUMENT_TYPE: Final[str] = "CC"


def main() -> None:
    """
    Entry point of the application.

    Establishes the session with the Campus Virtual endpoint, authenticates
    the user with the stored credentials, extracts the user profile from
    the profile page and displays it as a table.

    Returns:
        None
    """
    log("INFO", Tags.MAIN, "Starting KarlosKalendar...")

    client: CampusClient = CampusClient()
    client.establish_session()

    document_id: str = os.getenv("CC", "")
    password: str = os.getenv("PASSWORD", "")

    log("INFO", Tags.MAIN, "Authenticating on the Campus Virtual...")
    client.login(DOCUMENT_TYPE, document_id, password)

    html: str = client.fetch_profile_page()
    profile: UserProfile = parse_user_profile(html)

    log("SUCCESS", Tags.MAIN, f"Profile of {profile.full_name} (id {profile.user_id})")
    log("INFO", Tags.MAIN, _build_table(_profile_rows(profile)))


def _profile_rows(profile: UserProfile) -> List[Tuple[str, str]]:
    """
    Map a UserProfile into label/value rows for the table.

    Args:
        profile (UserProfile): Parsed profile data.

    Returns:
        list: Pairs of (label, value).
    """
    return [
        ("ID usuario", str(profile.user_id)),
        ("Tipo documento", profile.document_type),
        ("Documento", profile.document),
        ("Nombre completo", profile.full_name),
        ("Nombres y apellidos", _combine_names(profile)),
        ("Correo institucional", profile.institutional_email),
        ("Correo notificaciones", profile.notification_email),
        ("Correo personal", profile.personal_email),
        ("Telefono", profile.phone),
        ("Fecha nacimiento", profile.birth_date),
        ("Estado civil", profile.marital_status),
        ("RH", profile.blood_type),
        ("Zona", profile.zone),
        ("Estrato", profile.stratum),
        ("Direccion", profile.address),
    ]


def _combine_names(profile: UserProfile) -> str:
    """
    Join the first/second names and surnames of a profile into one string.

    Args:
        profile (UserProfile): Parsed profile data.

    Returns:
        str: The combined name, or an empty string if no part is present.
    """
    parts: List[str] = [
        profile.first_name,
        profile.second_name,
        profile.first_surname,
        profile.second_surname,
    ]
    return " ".join(part for part in parts if part)


def _build_table(rows: List[Tuple[str, str]]) -> str:
    """
    Render a list of label/value pairs as an ASCII table.

    Args:
        rows (list): Pairs of (label, value).

    Returns:
        str: The table as a single multi-line string.
    """
    label_width: int = max(len(label) for label, _ in rows)
    value_width: int = max(len(value) for _, value in rows)
    border: str = f"+{'-' * (label_width + 2)}+{'-' * (value_width + 2)}+"
    header: str = f"| {'Campo'.ljust(label_width)} | {'Valor'.ljust(value_width)} |"
    body: List[str] = [border, header, border]
    for label, value in rows:
        body.append(f"| {label.ljust(label_width)} | {value.ljust(value_width)} |")
        body.append(border)
    return "\n".join(body)


if __name__ == "__main__":
    main()