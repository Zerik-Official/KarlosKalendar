"""
Logger personalizado con soporte para etiquetas (tags) y niveles de log.
Permite filtrar por etiquetas y niveles, y es seguro para uso en múltiples hilos.
"""

# Standard library
import threading
from enum import StrEnum, unique
from typing import Literal, Final, Set, Dict
from datetime import datetime

# Third-party
from colorama import Fore, Style


# Lock global para logger, evitará los problemas de concurrencia.
_log_lock = threading.Lock()

# Si tiene tags, solo muestra esos tags. Vacío = muestra todos.
ENABLED_TAGS: Final[Set[str]] = set()

# Niveles ignorados globalmente para todos los tags.
DISABLED_LEVELS: Final[Set[str]] = set()

# Reglas por tag: define qué niveles IGNORAR para un tag específico.
# Ejemplo: "LOADER": {"DEBUG"} -> silencia DEBUG solo del LOADER
TAG_LEVEL_RULES: Dict[str, Set[str]] = {
}

LogLevel = Literal["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG", "CRITICAL"]

@unique
class Tags(StrEnum):
    MAIN = "MAIN"


def log(level: LogLevel, tag: Tags | str, message: str) -> None:
    """
    Imprime un mensaje de log con filtros por etiqueta y nivel.

    Args:
        level (str): Nivel del log (INFO, SUCCESS, WARNING, ERROR, DEBUG, CRITICAL).
        tag (str): Etiqueta del módulo (ej: MAIN, CORE, Navegador).
        message (str): Mensaje a imprimir en consola.
    Returns:
        None
    """
    level_up: str = level.upper()
    tag_up: str = tag.upper()

    if level_up in DISABLED_LEVELS:
        return

    if ENABLED_TAGS and tag_up not in ENABLED_TAGS:
        return

    if tag_up in TAG_LEVEL_RULES and level_up in TAG_LEVEL_RULES[tag_up]:
        return

    timestamp: str = datetime.now().strftime("%H:%M:%S")

    colors: Final[Dict[str, str]] = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.MAGENTA,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    color: str = colors.get(level_up, Fore.WHITE)

    lvl_fmt: str = f"{level_up:^9}"
    tag_fmt: str = f"{tag_up:^20}"

    with _log_lock:
        print(
            f"{Style.DIM}{timestamp}{Style.RESET_ALL} "
            f"[{color}{lvl_fmt}{Style.RESET_ALL}] "
            f"[{Fore.WHITE}{Style.BRIGHT}{tag_fmt}{Style.RESET_ALL}] "
            f"{message}"
        )