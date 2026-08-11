"""
Helpers to build and parse xajax (0.5) requests and responses.

The UNAD Campus portal uses xajax for its AJAX calls. Requests are sent
as form-encoded fields (xjxfun, xjxr, xjxargs[]) and responses are JSON.
"""

# Standard library
import json
import time
from typing import Any, Dict, Final, List

# Project imports
from schemas.schemas import XajaxCommand


# xajax functions used by the Campus portal.
LOGIN_REVISA_DOC: Final[str] = "f17_Login_RevisaDoc"


def build_request_body(
    function_name: str, args: List[Any], request_number: int | None = None
) -> Dict[str, str]:
    """
    Build the form-encoded body of an xajax request.

    Args:
        function_name (str): xajax function to invoke (xjxfun).
        args (list): Arguments array passed to the function.
        request_number (int | None): Optional request number (xjxr).

    Returns:
        dict: POST form data to send with the request.
    """
    number: int = request_number if request_number is not None else int(time.time() * 1000)
    return {
        "xjxfun": function_name,
        "xjxr": str(number),
        "xjxargs[]": json.dumps(args),
    }


def parse_response(text: str) -> List[XajaxCommand]:
    """
    Parse an xajax JSON response into a list of commands.

    Args:
        text (str): Raw response body.

    Returns:
        list: Parsed xajax commands.

    Raises:
        ValueError: If the response body is not valid JSON.
    """
    try:
        payload: dict = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("The xajax response is not valid JSON.") from exc

    commands: List[XajaxCommand] = []
    for item in payload.get("xjxobj", []):
        commands.append(
            XajaxCommand(
                cmd=str(item.get("cmd", "")),
                command_id=str(item.get("id", "")),
                prop=str(item.get("prop", "")),
                data=str(item.get("data", "")),
            )
        )
    return commands


def get_assign_value(commands: List[XajaxCommand], element_id: str) -> str | None:
    """
    Get the assigned value (data) of an "as" command for a given element id.

    Args:
        commands (list): Parsed xajax commands.
        element_id (str): Id of the target element (e.g. id11).

    Returns:
        str | None: The data assigned to the element, or None if not found.
    """
    for command in commands:
        if (
            command.cmd == "as"
            and command.command_id == element_id
            and command.prop == "value"
        ):
            return command.data
    return None