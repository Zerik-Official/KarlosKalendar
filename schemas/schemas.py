"""
Shared type definitions for KarlosKalendar.

Contains the frozen dataclasses and type aliases used across the
application (parsed portal data, xajax command models and log levels).
"""

# Standard library
from dataclasses import dataclass
from typing import List, Literal


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


@dataclass(frozen=True)
class AgendaActivity:
    """
    A single activity of an agenda section.

    Attributes:
        moment (str): Evaluation moment (Inicial, Intermedio, Final).
        rac (str): Learning outcome (RAC).
        name (str): Activity name.
        description (str): Activity description.
        activity_type (str): Activity type (Independiente, Laboratorio, etc).
        weight (str): Evaluative weight in points.
        start (str): Activity start date.
        end (str): Activity end date.
        alert (str): Closing alert.
        feedback (str): Feedback delivery date range.
    """

    moment: str
    rac: str
    name: str
    description: str
    activity_type: str
    weight: str
    start: str
    end: str
    alert: str
    feedback: str


@dataclass(frozen=True)
class AgendaSection:
    """
    A group of activities under a section header.

    Attributes:
        title (str): Section title (e.g. "Actividades correspondientes al 75%").
        activities (list): Activities of the section.
    """

    title: str
    activities: List[AgendaActivity]


@dataclass(frozen=True)
class CalendarAgenda:
    """
    Parsed data of an agenda page.

    Attributes:
        code (str): Numeric agenda code (e.g. 212014).
        name (str): Course name.
        credits (str): Credits text (e.g. "(TP) - 212014 de 2 créditos").
        period (str): Academic period (e.g. "2026 II PERIODO 16-04 (2204)").
        sections (list): Agenda sections with their activities.
    """

    code: str
    name: str
    credits: str
    period: str
    sections: List[AgendaSection]


@dataclass(frozen=True)
class AppConfig:
    """
    Application configuration.

    Attributes:
        interval_minutes (int): Minutes between scrape cycles.
        calendars (list): Registered agenda URLs to scrape.
    """

    interval_minutes: int
    calendars: List[str]


LogLevel = Literal["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
