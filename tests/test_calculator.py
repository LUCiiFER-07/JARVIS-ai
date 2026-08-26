import pytest

from core.calculator import calculate


def test_calculate_addition() -> None:
    assert calculate("5 + 3") == 8


def test_calculate_subtraction() -> None:
    assert calculate("10 - 4") == 6


def test_calculate_multiplication() -> None:
    assert calculate("6 * 7") == 42


def test_calculate_division() -> None:
    assert calculate("20 / 5") == 4


def test_calculate_decimal() -> None:
    assert calculate("2.5 + 1.5") == 4


def test_calculate_division_by_zero() -> None:
    with pytest.raises(ZeroDivisionError):
        calculate("10 / 0")


def test_calculate_invalid_expression() -> None:
    with pytest.raises(ValueError):
        calculate("hello world")