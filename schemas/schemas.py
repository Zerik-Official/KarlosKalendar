"""
Shared type definitions for KarlosKalendar.

Contains the frozen dataclasses and type aliases used across the
application (parsed portal data, xajax command models and log levels).
"""

# Standard library
from dataclasses import dataclass
from typing import Literal


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
    User data extracted from the profile page.

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


@dataclass(frozen=True)
class XajaxCommand:
    """
    A single command of an xajax JSON response.

    Attributes:
        cmd (str): Command type (as, js, etc).
        command_id (str): Id of the target element.
        prop (str): Property being assigned.
        data (str): Payload of the command.
    """

    cmd: str
    command_id: str
    prop: str
    data: str


LogLevel = Literal["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
