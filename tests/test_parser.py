"""
Test for the JARVIS command parser.
"""

import pytest

from core.commands import CommandType
from core.parser import CommandParser


@pytest.mark.parametrize(
    "text",
    [
        "Hello",
        "Hi",
        "Hey",
        "Hello Jarvis",
        "Hi Jarvis",
        "Hey Jarvis",
        "Jarvis hello",
        "Jarvis hi",
        "Jarvis hey",
        "Hello, Jarvis.",
        "Hi, Jarvis!",
    ],
)
def test_greeting_positive(text: str) -> None:
    """Test that valid greetings are detected correctly."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.GREETING


@pytest.mark.parametrize(
    "text",
    [
        "Please say hello",
        "I said hello yesterday",
        "Can you say hello to John?",
        "Hello was the first word I learned",
    ],
)
def test_greeting_negative(text: str) -> None:
    """Test that conversational greeting-containing phrases remain UNKNOWN."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.UNKNOWN


@pytest.mark.parametrize(
    "text",
    [
        "What time is it?",
        "What time it is?",
        "What's the time?",
        "Whats the time?",
        "What is the time?",
        "Tell me the time",
        "Current time",
        "Time please",
        "Can you tell me the time?",
        "Please tell me the current time",
        "What’s the time?",
    ],
)
def test_time_positive(text: str) -> None:
    """Test that time requests are detected correctly."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.GET_TIME


@pytest.mark.parametrize(
    "text",
    [
        "I had a good time yesterday",
        "Stop talking about time",
        "Time flies quickly",
        "We had time to finish",
        "I don't have time",
    ],
)
def test_time_negative(text: str) -> None:
    """Test that casual mentions of time remain UNKNOWN."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.UNKNOWN


@pytest.mark.parametrize(
    "text",
    [
        "Bye",
        "Bye Jarvis",
        "Bye, Jarvis.",
        "Goodbye",
        "Goodbye Jarvis",
        "Exit",
        "Quit",
        "Shutdown",
        "Stop Jarvis",
        "Jarvis stop",
        "Please stop",
    ],
)
def test_exit_positive(text: str) -> None:
    """Test that exit/stop requests are detected correctly."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.EXIT


@pytest.mark.parametrize(
    "text",
    [
        "Stop talking about time",
        "Stop making calculations",
        "Please stop talking about cars",
        "I said stop yesterday",
    ],
)
def test_exit_negative(text: str) -> None:
    """Test that conditional or conversational stop phrases remain UNKNOWN."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.UNKNOWN


@pytest.mark.parametrize(
    "text",
    [
        "5 + 7",
        "25 * 8",
        "10 / 2",
        "10 - 3",
        "2.5 + 1.5",
        "-5 + 3",
        "5 * -2",
        "-2.5 / 5",
        "5 plus 7",
        "5 add 7",
        "10 minus 3",
        "10 subtract 3",
        "5 times 4",
        "5 multiply 4",
        "5 multiplied by 4",
        "10 divide 2",
        "10 divided by 2",
        "2.5 plus 1.5",
        "Add 5 and 7",
        "Subtract 3 from 10",
        "Multiply 5 by 4",
        "Divide 10 by 2",
        "Calculate 5 plus 7",
        "Compute 10 divided by 2",
        "Solve 5 times 4",
        "What is 5 plus 7?",
        "Calculate nothing",
        "Calculate",
        "Compute",
        "Solve",
    ],
)
def test_calculation_positive(text: str) -> None:
    """Test that valid calculation expressions are detected correctly."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.CALCULATE


@pytest.mark.parametrize(
    "text",
    [
        "Twenty plus five",
        "five plus seven",
        "minus 5 plus 3",
        "5 + 3 + 2",
        "(5 + 3) * 2",
        "5 plus 3 plus 2",
        "Times are changing",
        "Divide and conquer",
        "Add some music later",
        "Subtract something later",
        "Solve world hunger",
        "Solve my problem",
        "Compute the weather",
        "Compute something unrelated",
        "Calculate my future",
        "Calculate the weather",
    ],
)
def test_calculation_negative(text: str) -> None:
    """Test that unsupported or conversational math phrases remain UNKNOWN."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.UNKNOWN


@pytest.mark.parametrize(
    "text",
    [
        "Hello and calculate 5 plus 5",
        "Stop talking about time",
        "I had a good time yesterday",
        "Open the moon",
    ],
)
def test_collisions_and_multi_intent(text: str) -> None:
    """Test that multi-intent sentences and false positives resolve to UNKNOWN."""
    command = CommandParser.parse(text)
    assert command.command_type == CommandType.UNKNOWN


def test_raw_text_preservation() -> None:
    """Test that raw Command.text is preserved verbatim without normalization changes."""
    raw1 = "Hello, Jarvis."
    cmd1 = CommandParser.parse(raw1)
    assert cmd1.command_type == CommandType.GREETING
    assert cmd1.text == raw1

    raw2 = "What is 2.5 plus 1.5?"
    cmd2 = CommandParser.parse(raw2)
    assert cmd2.command_type == CommandType.CALCULATE
    assert cmd2.text == raw2


def test_extra_whitespace() -> None:
    """Test that unnecessary whitespace is normalized for matching but raw text preserved."""
    raw = "  hello   Jarvis   "
    command = CommandParser.parse(raw)
    assert command.command_type == CommandType.GREETING
    assert command.text == raw


def test_empty_and_invalid_command() -> None:
    """Test that empty or invalid inputs are handled safely."""
    assert CommandParser.parse("").command_type == CommandType.UNKNOWN
    assert CommandParser.parse(None).command_type == CommandType.UNKNOWN
    assert CommandParser.parse("   ").command_type == CommandType.UNKNOWN
