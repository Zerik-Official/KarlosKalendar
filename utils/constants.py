from typing_extensions import Final

# Endpoint used by the HTML for the credentials (xajax requestURI).
BASE_URL: Final[str] = "https://campus0a.unad.edu.co/campus/"

# Authenticated profile page.
PROFILE_PATH: Final[str] = "perfilusuario.php"

# Name of the cookie that holds the server session id.
SSID_COOKIE: Final[str] = "PHPSESSID"

# Name of the cookie that stores the authenticated user id.
USER_ID_COOKIE: Final[str] = "idUsuario"

# Timeout in seconds for HTTP requests.
REQUEST_TIMEOUT: Final[int] = 30

# Default headers to simulate a browser.
DEFAULT_HEADERS: Final[dict] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}

# Document type used for the portal login.
DOCUMENT_TYPE: Final[str] = "CC"