"""
Utilities to parse the UNAD Campus pages.

Uses BeautifulSoup to extract user data from the HTML returned by the
portal (access page and profile page).
"""

# Third-party
from bs4 import BeautifulSoup, Tag

# Project imports
from schemas.schemas import UserInfo, UserProfile
from utils.log import log, Tags


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
        raise ValueError("#idusuario element not found in the page.")
    if name_element is None:
        raise ValueError(".nav__user__name element not found in the page.")

    user_id: int = int(str(user_id_input["value"]))
    name: str = name_element.get_text(strip=True)

    log("INFO", Tags.PARSER, f"User parsed: id={user_id}, name={name}")
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
        raise ValueError("#unad11id element not found in the page.")

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

    log("INFO", Tags.PARSER, f"Profile parsed: id={user_id}, name={profile.full_name}")
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