"""
Command models fro JARVIS.
"""

from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """
    Supported JARVIS command types.
    """

    UNKNOWN = "unknown"
    GREETING = "greeting"
    CALCULATE = "calculate"
    GET_TIME = "get_time"
    EXIT = "exit"


@dataclass(slots=True)
class Command:
    """
    Represent a parsed user command.
    """

    command_type: CommandType
    text: str
    confidence: float = 1.0