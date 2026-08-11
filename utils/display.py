"""
Display helpers for the CLI output.

Renders the user profile as a Rich table.
"""

# Standard library
from typing import List, Tuple

# Third-party
from rich.console import Console
from rich.table import Table

# Project imports
from schemas.schemas import UserProfile


def print_profile(profile: UserProfile) -> None:
    """
    Print the profile data as a Rich table.

    Args:
        profile (UserProfile): Parsed profile data.

    Returns:
        None
    """
    console: Console = Console()

    table: Table = Table(show_header=False, box=None, padding=(0, 1))

    table.add_column("Campo", style="cyan")
    table.add_column("Valor")

    for label, value in profile_rows(profile):
        table.add_row(label, value)

    console.print(table)


def profile_rows(profile: UserProfile) -> List[Tuple[str, str]]:
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


def combine_names(profile: UserProfile) -> str:
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
