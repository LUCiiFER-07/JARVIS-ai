"""
Tests for the JARVIS command executor and math normalizer integration.
"""

import pytest

from core.commands import Command, CommandType
from core.executor import CommandExecutor


@pytest.mark.parametrize(
    "text,expected",
    [
        ("5 + 7", "The answer is 12."),
        ("25 * 8", "The answer is 200."),
        ("10 / 2", "The answer is 5."),
        ("10 - 3", "The answer is 7."),
        ("2.5 + 1.5", "The answer is 4."),
        ("-5 + 3", "The answer is -2."),
        ("5 * -2", "The answer is -10."),
        ("-2.5 / 5", "The answer is -0.5."),
    ],
)
def test_symbolic_execution(text: str, expected: str) -> None:
    """Test execution of symbolic calculations."""
    executor = CommandExecutor()
    command = Command(command_type=CommandType.CALCULATE, text=text)
    assert executor.execute(command) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("5 plus 7", "The answer is 12."),
        ("5 add 7", "The answer is 12."),
        ("10 minus 3", "The answer is 7."),
        ("10 subtract 3", "The answer is 7."),
        ("5 times 4", "The answer is 20."),
        ("5 multiply 4", "The answer is 20."),
        ("5 multiplied by 4", "The answer is 20."),
        ("10 divide 2", "The answer is 5."),
        ("10 divided by 2", "The answer is 5."),
        ("2.5 plus 1.5", "The answer is 4."),
    ],
)
def test_spoken_infix_execution(text: str, expected: str) -> None:
    """Test execution of spoken infix calculations."""
    executor = CommandExecutor()
    command = Command(command_type=CommandType.CALCULATE, text=text)
    assert executor.execute(command) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Add 5 and 7", "The answer is 12."),
        ("Subtract 3 from 10", "The answer is 7."),
        ("Multiply 5 by 4", "The answer is 20."),
        ("Divide 10 by 2", "The answer is 5."),
    ],
)
def test_imperative_execution(text: str, expected: str) -> None:
    """Test execution of imperative calculations with correct operand ordering."""
    executor = CommandExecutor()
    command = Command(command_type=CommandType.CALCULATE, text=text)
    assert executor.execute(command) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Calculate 5 plus 7", "The answer is 12."),
        ("Compute 10 divided by 2", "The answer is 5."),
        ("Solve 5 times 4", "The answer is 20."),
        ("What is 5 plus 7?", "The answer is 12."),
    ],
)
def test_prefixed_execution(text: str, expected: str) -> None:
    """Test execution of prefixed calculations."""
    executor = CommandExecutor()
    command = Command(command_type=CommandType.CALCULATE, text=text)
    assert executor.execute(command) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Calculate",
        "Compute",
        "Solve",
        "Calculate nothing",
        "",
        "   ",
        "  Calculate  ",
        "COMPUTE",
    ],
)
def test_no_expression_calculation(text: str) -> None:
    """Test explicit calculation requests with no expression return established response."""
    executor = CommandExecutor()
    command = Command(command_type=CommandType.CALCULATE, text=text)
    assert executor.execute(command) == "I could not find a calculation to perform."


@pytest.mark.parametrize(
    "text",
    [
        "hello",
        "5 plus",
        "5 +",
        "Twenty plus five",
        "Compute nothing",
        "Solve nothing",
    ],
)
def test_malformed_calculation(text: str) -> None:
    """Test malformed calculations return established invalid-calculation response."""
    executor = CommandExecutor()
    command = Command(command_type=CommandType.CALCULATE, text=text)
    assert executor.execute(command) == "I could not understand that calculation."


@pytest.mark.parametrize(
    "text",
    [
        "10 / 0",
        "Divide 10 by 0",
    ],
)
def test_division_by_zero(text: str) -> None:
    """Test safe handling of division by zero."""
    executor = CommandExecutor()
    command = Command(command_type=CommandType.CALCULATE, text=text)
    assert executor.execute(command) == "I cannot divide by zero."


def test_non_calculation_regression() -> None:
    """Ensure non-calculation command behavior remains unchanged."""
    executor = CommandExecutor()

    # Greeting
    greeting_cmd = Command(command_type=CommandType.GREETING, text="hello jarvis")
    assert executor.execute(greeting_cmd) == "HELLO, SIR! How can I help you?"

    # Get Time
    time_cmd = Command(command_type=CommandType.GET_TIME, text="what time is it")
    assert executor.execute(time_cmd).startswith("The current time is ")

    # Exit
    exit_cmd = Command(command_type=CommandType.EXIT, text="goodbye")
    assert executor.execute(exit_cmd) == "Goodbye, Sir."

    # Unknown
    unknown_cmd = Command(command_type=CommandType.UNKNOWN, text="open the moon")
    assert executor.execute(unknown_cmd) == "Sorry, I don't understand that command."
