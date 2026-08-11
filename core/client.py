"""
HTTP client for the UNAD Campus portal.

Manages the persistent session (requests.Session), the xajax login
flow and the authenticated navigation through the portal pages.
"""

# Standard library
import base64

# Third-party
import requests
from bs4 import BeautifulSoup, Tag

# Project imports
from core.xajax import (
    LOGIN_REVISA_DOC,
    XajaxCommand,
    build_request_body,
    get_assign_value,
    parse_response,
)
from utils.constants import (
    BASE_URL,
    DEFAULT_HEADERS,
    PROFILE_PATH,
    REQUEST_TIMEOUT,
    SSID_COOKIE,
)
from utils.log import log, Tags


class CampusClient:
    """
    Persistent HTTP client against the UNAD Campus portal.

    Attributes:
        session (requests.Session): Persistent session that keeps cookies.
        ssid (str | None): Session id (PHPSESSID) obtained from the server.
        user_id (int | None): Id of the authenticated user.
    """

    def __init__(self) -> None:
        """Initialize the HTTP session and the session attributes."""
        self.session: requests.Session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.ssid: str | None = None
        self.user_id: int | None = None
        self._landing_html: str | None = None

    def establish_session(self) -> str | None:
        """
        Perform the first request to the campus endpoint and capture the SSID.

        Returns:
            str | None: The SSID cookie value received from the server,
                or None if the server did not issue it.
        """
        response: requests.Response = self.session.get(
            BASE_URL, timeout=REQUEST_TIMEOUT
        )
        self._landing_html = response.text
        log("INFO", Tags.CLIENT, f"First request, status: {response.status_code}")

        self.ssid = self.session.cookies.get(SSID_COOKIE)
        if self.ssid is not None:
            log("SUCCESS", Tags.CLIENT, f"Session established, SSID: {self.ssid}")
        else:
            log("ERROR", Tags.CLIENT, "The server did not return the session cookie.")

        return self.ssid

    def login(self, document_type: str, document_id: str, password: str) -> int | None:
        """
        Authenticate the session through the xajax login function.

        Follows the saltos navigation flow and posts the credentials to
        the login endpoint. Stores the authenticated user id.

        Args:
            document_type (str): Document type code (CC, TI, CE, etc).
            document_id (str): Document number of the user.
            password (str): Plain text password of the user.

        Returns:
            int | None: The authenticated user id, or None on failure.
        """
        if self.ssid is None:
            self.establish_session()

        self._follow_saltos()

        encoded_password: str = base64.b64encode(password.encode("utf-8")).decode("ascii")
        body: dict = build_request_body(
            LOGIN_REVISA_DOC, [document_type, document_id, encoded_password, "0"]
        )
        response: requests.Response = self.session.post(
            BASE_URL, data=body, timeout=REQUEST_TIMEOUT
        )

        try:
            commands: list[XajaxCommand] = parse_response(response.text)
        except ValueError as exc:
            log("ERROR", Tags.LOGIN, f"The login response was not JSON: {exc}")
            return None

        user_id_value: str | None = get_assign_value(commands, "id11")
        if user_id_value is None:
            log("ERROR", Tags.LOGIN, "The login did not return the user id.")
            return None

        self.user_id = int(user_id_value)
        log("SUCCESS", Tags.LOGIN, f"Login successful, user_id: {self.user_id}")
        return self.user_id

    def fetch_profile_page(self) -> str:
        """
        Get the profile page (perfilusuario.php) of the authenticated user.

        Returns:
            str: Raw HTML content of the profile page.
        """
        response: requests.Response = self.session.get(
            BASE_URL + PROFILE_PATH, timeout=REQUEST_TIMEOUT
        )
        log(
            "INFO",
            Tags.CLIENT,
            f"Profile fetched, status: {response.status_code}, bytes: {len(response.text)}",
        )
        return response.text

    def _follow_saltos(self) -> None:
        """
        Follow the saltos (anti-popup) loop until the login form is served.

        The first request returns an intermediate page that POSTs a "base"
        value with an incrementing "saltos" counter. Repeating the POST with
        only the saltos value eventually serves the real login page.

        Returns:
            None
        """
        if self._landing_html is None:
            return

        soup: BeautifulSoup = BeautifulSoup(self._landing_html, "html.parser")
        base_input: Tag | None = soup.select_one("input#base")
        saltos_input: Tag | None = soup.select_one("input#saltos")
        base: str = str(base_input["value"]) if base_input and base_input.get("value") else ""
        saltos: int = int(str(saltos_input["value"])) if saltos_input and saltos_input.get("value") else 1

        for index in range(10):
            data: dict = (
                {"base": base, "saltos": str(saltos)}
                if index == 0
                else {"saltos": str(saltos)}
            )
            response: requests.Response = self.session.post(
                BASE_URL, data=data, timeout=REQUEST_TIMEOUT
            )
            if "frmedita" in response.text:
                return

            next_soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
            next_saltos: Tag | None = next_soup.select_one("input#saltos")
            if next_saltos is None or not next_saltos.get("value"):
                return
            saltos = int(str(next_saltos["value"]))