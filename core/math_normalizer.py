"""
Deterministic math expression normalizer for JARVIS.
"""

import re


def normalize_math_expression(text: str) -> str:
    """
    Convert raw calculation text or spoken math into one safe symbolic binary expression.

    Args:
        text: Raw calculation text.

    Returns:
        Normalized symbolic binary expression (e.g., "5 + 7").

    Raises:
        ValueError: If the input is unsupported, malformed, or cannot be parsed.
    """
    if not text or not isinstance(text, str):
        raise ValueError("Invalid math expression: input must be a non-empty string.")

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Invalid math expression: input is empty.")

    # Remove terminal sentence punctuation safely (question marks, exclamation marks, trailing periods)
    # while preserving decimal points and negative signs.
    cleaned = re.sub(r"[?!.]+$", "", cleaned).strip()

    if not cleaned:
        raise ValueError("Invalid math expression: empty after punctuation stripping.")

    # Remove common calculation prefixes (case-insensitive) operating on cleaned string directly.
    cleaned = re.sub(r"^(?:calculate|compute|solve|what\s+is)\s+", "", cleaned, flags=re.IGNORECASE).strip()

    if not cleaned:
        raise ValueError("Invalid math expression: empty after prefix removal.")

    cleaned_lower = cleaned.lower()

    # -------------------------------------------------
    # 1. Imperative / Natural sentence patterns
    # -------------------------------------------------
    # "add 5 and 7" -> "5 + 7"
    match = re.fullmatch(
        r"add\s+(-?\d+(?:\.\d+)?)\s+and\s+(-?\d+(?:\.\d+)?)",
        cleaned_lower,
    )
    if match:
        left, right = match.groups()
        return f"{left} + {right}"

    # "subtract 3 from 10" -> "10 - 3"
    match = re.fullmatch(
        r"subtract\s+(-?\d+(?:\.\d+)?)\s+from\s+(-?\d+(?:\.\d+)?)",
        cleaned_lower,
    )
    if match:
        amount, original = match.groups()
        return f"{original} - {amount}"

    # "multiply 5 by 4" -> "5 * 4"
    match = re.fullmatch(
        r"multiply\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)",
        cleaned_lower,
    )
    if match:
        left, right = match.groups()
        return f"{left} * {right}"

    # "divide 10 by 2" -> "10 / 2"
    match = re.fullmatch(
        r"divide\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)",
        cleaned_lower,
    )
    if match:
        left, right = match.groups()
        return f"{left} / {right}"

    # -------------------------------------------------
    # 2. Spoken infix expressions (e.g. "5 plus 7", "5 add 7", "10 subtract 3")
    # -------------------------------------------------
    spoken_text = cleaned_lower

    # Replace multi-word spoken operators first
    spoken_text = re.sub(r"\bmultiplied\s+by\b", "*", spoken_text)
    spoken_text = re.sub(r"\bmultiply\s+by\b", "*", spoken_text)
    spoken_text = re.sub(r"\bdivided\s+by\b", "/", spoken_text)

    # Replace single-word operators, including "add" and "subtract" infix
    replacements = (
        (r"\bplus\b", "+"),
        (r"\badd\b", "+"),
        (r"\bminus\b", "-"),
        (r"\bsubtract\b", "-"),
        (r"\btimes\b", "*"),
        (r"\bmultiply\b", "*"),
        (r"\bdivide\b", "/"),
    )
    for pattern, replacement in replacements:
        spoken_text = re.sub(pattern, f" {replacement} ", spoken_text)

    # Clean up whitespace
    spoken_text = re.sub(r"\s+", " ", spoken_text).strip()

    # -------------------------------------------------
    # 3. Validate against final safe binary expression pattern
    # -------------------------------------------------
    binary_pattern = (
        r"^([-+]?\d+(?:\.\d+)?)"
        r"\s*([+\-*/])\s*"
        r"([-+]?\d+(?:\.\d+)?)$"
    )

    match = re.fullmatch(binary_pattern, spoken_text)
    if not match:
        raise ValueError(f"Invalid math expression: '{text}' cannot be normalized to a binary expression.")

    left, symbol, right = match.groups()
    return f"{left} {symbol} {right}"
