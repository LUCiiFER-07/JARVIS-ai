"""
Tests for deterministic math normalizer.
"""

import pytest

from core.calculator import calculate
from core.math_normalizer import normalize_math_expression


@pytest.mark.parametrize(
    "input_expr,expected",
    [
        ("5 + 7", "5 + 7"),
        ("25 * 8", "25 * 8"),
        ("10 / 2", "10 / 2"),
        ("10 - 3", "10 - 3"),
        ("2.5 + 1.5", "2.5 + 1.5"),
        ("-5 + 3", "-5 + 3"),
        ("5 * -2", "5 * -2"),
        ("-2.5 / 5", "-2.5 / 5"),
        ("  5+7  ", "5 + 7"),
    ],
)
def test_symbolic_expressions(input_expr, expected):
    """Verify symbolic expressions normalize correctly."""
    assert normalize_math_expression(input_expr) == expected
    assert calculate(normalize_math_expression(input_expr)) is not None


@pytest.mark.parametrize(
    "input_expr,expected",
    [
        ("5 plus 7", "5 + 7"),
        ("5 add 7", "5 + 7"),
        ("10 minus 3", "10 - 3"),
        ("10 subtract 3", "10 - 3"),
        ("5 times 4", "5 * 4"),
        ("5 multiply 4", "5 * 4"),
        ("5 multiplied by 4", "5 * 4"),
        ("10 divided by 2", "10 / 2"),
        ("2.5 plus 1.5", "2.5 + 1.5"),
    ],
)
def test_spoken_infix_expressions(input_expr, expected):
    """Verify spoken infix expressions normalize correctly."""
    assert normalize_math_expression(input_expr) == expected
    assert calculate(normalize_math_expression(input_expr)) is not None


@pytest.mark.parametrize(
    "input_expr,expected",
    [
        ("Add 5 and 7", "5 + 7"),
        ("Subtract 3 from 10", "10 - 3"),
        ("Multiply 5 by 4", "5 * 4"),
        ("Divide 10 by 2", "10 / 2"),
    ],
)
def test_imperative_expressions(input_expr, expected):
    """Verify imperative expressions normalize correctly with proper operand ordering."""
    assert normalize_math_expression(input_expr) == expected
    assert calculate(normalize_math_expression(input_expr)) is not None


@pytest.mark.parametrize(
    "input_expr,expected",
    [
        ("Calculate 5 plus 7", "5 + 7"),
        ("Compute 10 divided by 2", "10 / 2"),
        ("Solve 5 times 4", "5 * 4"),
        ("What is 5 plus 7?", "5 + 7"),
        ("CALCULATE 25 * 8", "25 * 8"),
        ("  compute   10 minus 3  ", "10 - 3"),
    ],
)
def test_prefixed_expressions(input_expr, expected):
    """Verify prefixed expressions normalize correctly."""
    assert normalize_math_expression(input_expr) == expected


@pytest.mark.parametrize(
    "input_expr,expected",
    [
        ("What is 5 plus 7?", "5 + 7"),
        ("Calculate 5 plus 7.", "5 + 7"),
        ("Calculate 2.5 plus 1.5.", "2.5 + 1.5"),
        ("What is 10 divided by 2?!", "10 / 2"),
    ],
)
def test_terminal_punctuation(input_expr, expected):
    """Verify terminal punctuation is stripped while decimal points remain intact."""
    assert normalize_math_expression(input_expr) == expected


@pytest.mark.parametrize(
    "invalid_expr",
    [
        "Twenty plus five",
        "minus 5 plus 3",
        "5 + 3 + 2",
        "(5 + 3) * 2",
        "5 plus 3 plus 2",
        "Times are changing",
        "Divide and conquer",
        "Add some music later",
        "Subtract something later",
        "Calculate nothing",
        "hello",
        "",
        "   ",
        None,
        "5 and plus 7",
        "5 plus and 7",
        "5 plus 7 and",
    ],
)
def test_unsupported_input_raises_value_error(invalid_expr):
    """Verify unsupported or malformed input raises ValueError."""
    with pytest.raises(ValueError):
        normalize_math_expression(invalid_expr)
