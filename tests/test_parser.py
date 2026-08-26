"""
Test for the JARVIS command parser.
"""

from core.commands import CommandType
from core.parser import CommandParser


def test_greeting_command() -> None:
    """Test that greetings are detected correctly."""

    command = CommandParser.parse("Hello Jarvis")

    assert command.command_type == CommandType.GREETING
    assert command.text == "Hello Jarvis"

def test_time_command() -> None:
    """Test that time requests are detected correctly."""

    command = CommandParser.parse("What time is it?")

    assert command.command_type == CommandType.GET_TIME

def test_calculation_command() -> None:
    """Test that calculation requests are detected correctly"""

    command = CommandParser.parse("Calculate 25 * 8")

    assert command.command_type == CommandType.CALCULATE

def test_unknown_command() -> None:
    """Test thatunsupported commands are classified as unknown."""

    command = CommandParser.parse("Open the moon")

    assert command.command_type == CommandType.UNKNOWN

def test_empty_command() -> None:
    """Test that empty input is handled safely."""

    command = CommandParser.parse("")

    assert command.command_type == CommandType.UNKNOWN

def test_extra_whitespace() -> None:
    """test the unnecessary whitespace is normalized."""

    command = CommandParser.parse("  hello   Jarvis   ")

    assert command.command_type == CommandType.GREETING