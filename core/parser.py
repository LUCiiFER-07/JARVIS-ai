"""
Command parser for JARVIS.
"""

import re

from core.commands import Command, CommandType


class CommandParser:
    """
    Convert raw speech text into a structured Command.
    """

    @classmethod
    def parse(cls, text: str) -> Command:
        """
        Parse raw speech text into a Command.

        Args:
            text:
                Raw text returned by speech recognition.

        Returns:
            A structured Command object.
        """
        if text is None or not isinstance(text, str):
            return Command(
                command_type=CommandType.UNKNOWN,
                text="" if text is None else str(text),
                confidence=1.0,
            )

        normalized = cls._normalize(text)

        if not normalized:
            return Command(
                command_type=CommandType.UNKNOWN,
                text=text,
                confidence=1.0,
            )

        if cls._is_greeting(normalized):
            return Command(
                command_type=CommandType.GREETING,
                text=text,
            )

        if cls._is_time_request(normalized):
            return Command(
                command_type=CommandType.GET_TIME,
                text=text,
            )

        if cls._is_calculation(normalized):
            return Command(
                command_type=CommandType.CALCULATE,
                text=text,
            )

        if cls._is_exit_request(normalized):
            return Command(
                command_type=CommandType.EXIT,
                text=text,
            )

        return Command(
            command_type=CommandType.UNKNOWN,
            text=text,
            confidence=0.5,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize user speech for intent matching while preserving arithmetic symbols,
        decimal points, and negative signs.
        """
        text = text.strip().lower()

        # Normalize specific contractions: what's / what’s -> what is
        text = re.sub(r"\bwhat['’]s\b", "what is", text)

        # Remove sentence punctuation (commas, question marks, exclamation marks, terminal periods)
        # while keeping arithmetic operators (+, -, *, /), decimal points (.), and digits/words.
        text = re.sub(r"[,?!]+", " ", text)
        text = re.sub(r"\.(?!\d)", " ", text)  # remove periods not part of decimals

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    @classmethod
    def _is_greeting(cls, text: str) -> bool:
        """
        Check whether the text is a greeting using bounded, anchored patterns.
        """
        pattern = r"^(?:hello|hi|hey)(?:\s+jarvis)?$|^jarvis\s+(?:hello|hi|hey)$"
        return bool(re.fullmatch(pattern, text, re.IGNORECASE))

    @classmethod
    def _is_time_request(cls, text: str) -> bool:
        """
        Check whether the user is asking for the time using bounded patterns.
        """
        pattern = (
            r"^(?:"
            r"what\s+time\s+is\s+it|"
            r"what\s+time\s+it\s+is|"
            r"what\s+is\s+the\s+time|"
            r"whats\s+the\s+time|"
            r"tell\s+me\s+the\s+time|"
            r"current\s+time|"
            r"time\s+please|"
            r"can\s+you\s+tell\s+me\s+the\s+time|"
            r"please\s+tell\s+me\s+the\s+current\s+time"
            r")$"
        )
        return bool(re.fullmatch(pattern, text, re.IGNORECASE))

    @classmethod
    def _is_calculation(cls, text: str) -> bool:
        """
        Check whether the text contains a basic calculation using bounded deterministic patterns.
        """
        # 1. Exact standalone explicit calculation request words (e.g. "Calculate")
        if re.fullmatch(r"^(?:calculate|compute|solve)$", text, re.IGNORECASE):
            return True

        # 2. Locked exception: "Calculate nothing" -> CALCULATE
        if re.fullmatch(r"^calculate\s+nothing$", text, re.IGNORECASE):
            return True

        # Strip optional arithmetic prefixes for further shape matching
        cleaned = re.sub(r"^(?:calculate|compute|solve|what\s+is)\s+", "", text, flags=re.IGNORECASE).strip()

        if not cleaned:
            return False

        # 3. Bare symbolic binary expression: operand op operand
        symbolic_pattern = (
            r"^([-+]?\d+(?:\.\d+)?)"
            r"\s*([+\-*/])\s*"
            r"([-+]?\d+(?:\.\d+)?)$"
        )
        if re.fullmatch(symbolic_pattern, cleaned):
            return True

        # 3. Spoken infix arithmetic: operand spoken_op operand
        spoken_infix_pattern = (
            r"^([-+]?\d+(?:\.\d+)?)"
            r"\s+(?:plus|add|minus|subtract|times|multiply|multiplied\s+by|divide|divided\s+by)\s+"
            r"([-+]?\d+(?:\.\d+)?)$"
        )
        if re.fullmatch(spoken_infix_pattern, cleaned, re.IGNORECASE):
            return True

        # 4. Imperative arithmetic shapes:
        return bool(
            re.fullmatch(r"add\s+(-?\d+(?:\.\d+)?)\s+and\s+(-?\d+(?:\.\d+)?)", cleaned, re.IGNORECASE)
            or re.fullmatch(r"subtract\s+(-?\d+(?:\.\d+)?)\s+from\s+(-?\d+(?:\.\d+)?)", cleaned, re.IGNORECASE)
            or re.fullmatch(r"multiply\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)", cleaned, re.IGNORECASE)
            or re.fullmatch(r"divide\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)", cleaned, re.IGNORECASE)
        )

    @classmethod
    def _is_exit_request(cls, text: str) -> bool:
        """
        Check whether the user wants JARVIS to stop using bounded patterns.
        """
        pattern = (
            r"^(?:"
            r"(?:bye|goodbye|exit|quit|shutdown)(?:\s+jarvis)?|"
            r"jarvis\s+stop|"
            r"(?:stop\s+jarvis|please\s+stop)"
            r")$"
        )
        return bool(re.fullmatch(pattern, text, re.IGNORECASE))
