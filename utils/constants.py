from typing_extensions import Final

# Endpoint que usa el HTML para las credenciales (requestURI de xajax).
BASE_URL: Final[str] = "https://campus0a.unad.edu.co/campus/"

# Página de perfil autenticada.
PROFILE_PATH: Final[str] = "perfilusuario.php"

# Nombre de la cookie que contiene el id de sesión del servidor.
SSID_COOKIE: Final[str] = "PHPSESSID"

# Nombre de la cookie que guarda el id del usuario autenticado.
USER_ID_COOKIE: Final[str] = "idUsuario"

# Timeout en segundos para las peticiones HTTP.
REQUEST_TIMEOUT: Final[int] = 30

# Cabeceras por defecto para simular un navegador.
DEFAULT_HEADERS: Final[dict] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}