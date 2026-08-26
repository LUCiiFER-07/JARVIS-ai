"""
Basic arithmetic calculator for JARVIS.
"""

import operator
import re

_OPERATIONS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def calculate(expression: str) -> int | float:
    """
    Safely calculate a basic arithmetic expression.
    
    Supported operators:
        +, -, *, /
        
    Args:
        expression:
                Arithmetic expressinsuch as "5 + 3".

    Returns:
        Calculated result.
                
    Raises:
        ValueError:
            If the expression is invalid.
        ZeroDivisionError:
            If division by zero is attempted.
    """


    expression = expression.strip()

    pattern = (
        r"^(-?\d+(?:\.\d+)?)"
        r"\s*([+\-*/])\s*"
        r"(-?\d+(?:\.\d+)?)$"
    )

    match = re.fullmatch(pattern, expression)

    if match is None:
        raise ValueError("Invalid arithmetic expression.")

    left, symbol, right = match.groups()

    left_number = float(left)

    right_number = float(right)


    if symbol =="/" and right_number == 0:
        raise ZeroDivisionError("Cannot divide by zero.")

    result = _OPERATIONS[symbol](
        left_number,
        right_number,
    )

    if result.is_integer():
        return int(result)

    return result