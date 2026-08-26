from core.commands import Command, CommandType
from core.executor import CommandExecutor


def test_greeting_command():
    executor = CommandExecutor()

    command = Command(
        command_type=CommandType.GREETING,
        text="hello jarvis",
    )

    executor = CommandExecutor()

    assert executor.execute(command) == "HELLO, SIR! How can I help you?"


def test_time_execution() -> None:
    command = Command(
        command_type=CommandType.GET_TIME,
        text="what time is it",
    )
    executor = CommandExecutor()

    result = executor.execute(command)

    assert result.startswith("The current time is ")


def test_unknown_execution() -> None:
    command = Command(
        command_type=CommandType.UNKNOWN,
        text="something random",
    )
    executor = CommandExecutor()

    assert(
        executor.execute(command)
        == "Sorry, I don't understand that command."
    )

def test_calculate_addition() -> None:
    command = Command(
        command_type=CommandType.CALCULATE,
        text="calculate 5 + 3",
    )

    executor = CommandExecutor()

    assert executor.execute(command) == "The answer is 8."


def test_calculate_multiplication() -> None:
    command = Command(
        command_type=CommandType.CALCULATE,
        text="calculate 6 * 7",
    )

    executor = CommandExecutor()

    assert executor.execute(command) == "The answer is 42."


def test_calculate_division_by_zero() -> None:
    command = Command(
        command_type=CommandType.CALCULATE,
        text="calculate 10 / 0",
    )

    executor = CommandExecutor()

    assert executor.execute(command) == "I cannot divide by zero."