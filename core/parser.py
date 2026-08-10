"""
Utilities to parse the UNAD Campus pages.

Uses BeautifulSoup to extract user data from the HTML returned by the
portal (access page and profile page).
"""

# Standard library
from dataclasses import dataclass

# Third-party
from bs4 import BeautifulSoup, Tag

# Project imports
from utils.log import log, Tags


@dataclass(frozen=True)
class UserInfo:
    """
    User data extracted from the access page.

    Attributes:
        user_id (int): Numeric user id (idusuario hidden input).
        name (str): Full display name of the user.
    """

    user_id: int
    name: str


@dataclass(frozen=True)
class UserProfile:
    """
    User data extracted from the profile page (perfilusuario.php).

    Attributes:
        user_id (int): Numeric user id.
        document_type (str): Document type code (CC, TI, etc).
        document (str): Document number.
        full_name (str): Full display name.
        first_name (str): First name.
        second_name (str): Second name.
        first_surname (str): First surname.
        second_surname (str): Second surname.
        institutional_email (str): UNAD institutional email.
        notification_email (str): Email used for notifications.
        personal_email (str): Personal email.
        phone (str): Phone number.
        birth_date (str): Birth date (dd/mm/yyyy).
        marital_status (str): Marital status.
        blood_type (str): Blood type (Rh).
        zone (str): Residential zone.
        stratum (str): Socio-economic stratum.
        address (str): Home address.
    """

    user_id: int
    document_type: str
    document: str
    full_name: str
    first_name: str
    second_name: str
    first_surname: str
    second_surname: str
    institutional_email: str
    notification_email: str
    personal_email: str
    phone: str
    birth_date: str
    marital_status: str
    blood_type: str
    zone: str
    stratum: str
    address: str


def parse_user_info(html: str) -> UserInfo:
    """
    Extract the user id and display name from the access page HTML.

    Args:
        html (str): Raw HTML content of the access page.

    Returns:
        UserInfo: The user id and name found in the page.

    Raises:
        ValueError: If the user id or the user name element is missing.
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    user_id_input: Tag | None = soup.select_one("input#idusuario")
    name_element: Tag | None = soup.select_one("div.nav__user__name span")

    if user_id_input is None or not user_id_input.get("value"):
        raise ValueError("Elemento #idusuario no encontrado en la pagina.")
    if name_element is None:
        raise ValueError("Elemento .nav__user__name no encontrado en la pagina.")

    user_id: int = int(str(user_id_input["value"]))
    name: str = name_element.get_text(strip=True)

    log("INFO", Tags.PARSER, f"Usuario parseado: id={user_id}, nombre={name}")
    return UserInfo(user_id=user_id, name=name)


def parse_user_profile(html: str) -> UserProfile:
    """
    Extract the user data from the profile page HTML.

    Args:
        html (str): Raw HTML content of the profile page.

    Returns:
        UserProfile: The user data found in the page.

    Raises:
        ValueError: If the required elements (user id or full name) are missing.
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    user_id: int = int(_input_value(soup, "input#unad11id") or "0")

    if user_id == 0:
        raise ValueError("Elemento #unad11id no encontrado en la pagina.")

    profile: UserProfile = UserProfile(
        user_id=user_id,
        document_type=_input_value(soup, "input#unad11tipodoc"),
        document=_input_value(soup, "input#unad11doc"),
        full_name=_input_value(soup, "input#unad11razonsocial"),
        first_name=_input_value(soup, "input#unad11nombre1"),
        second_name=_input_value(soup, "input#unad11nombre2"),
        first_surname=_input_value(soup, "input#unad11apellido1"),
        second_surname=_input_value(soup, "input#unad11apellido2"),
        institutional_email=_input_value(soup, "input#unad11correoinstitucional"),
        notification_email=_input_value(soup, "input#unad11correonotifica"),
        personal_email=_input_value(soup, "input#unad11correo"),
        phone=_input_value(soup, "input#unad11telefono"),
        birth_date=_input_value(soup, "input#unad11fechanace"),
        marital_status=_selected_option_text(soup, "select#unad11ecivil"),
        blood_type=_selected_option_text(soup, "select#unad11rh"),
        zone=_selected_option_text(soup, "select#unad01zonares"),
        stratum=_input_value(soup, "input#unad01estrato"),
        address=_input_value(soup, "input#unad11direccion"),
    )

    log("INFO", Tags.PARSER, f"Perfil parseado: id={user_id}, nombre={profile.full_name}")
    return profile


def _input_value(soup: BeautifulSoup, selector: str) -> str:
    """
    Get the value attribute of an input element identified by a selector.

    Args:
        soup (BeautifulSoup): Parsed HTML document.
        selector (str): CSS selector of the input element.

    Returns:
        str: The value attribute, or an empty string if missing.
    """
    element: Tag | None = soup.select_one(selector)
    if element is None or not element.get("value"):
        return ""
    return str(element["value"])


def _selected_option_text(soup: BeautifulSoup, selector: str) -> str:
    """
    Get the text of the selected option of a select element.

    Args:
        soup (BeautifulSoup): Parsed HTML document.
        selector (str): CSS selector of the select element.

    Returns:
        str: Text of the selected option, or an empty string if not found.
    """
    select: Tag | None = soup.select_one(selector)
    if select is None:
        return ""
    option: Tag | None = select.find("option", selected=True)
    if option is None:
        return ""
    return option.get_text(strip=True)