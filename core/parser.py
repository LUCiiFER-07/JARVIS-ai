"""
Command parser for JARVIS.
"""

import re

from core.commands import Command, CommandType


class CommandParser:
    """
    Convert raw speech text into a structured Command.
    """

    GREETING_WORDS = (
        "hello",
        "hi",
        "hey",
    )

    TIME_PHRASES = (
        "what time is it",
        "tell me the time",
        "current time",
        "what's the time",
    )

    EXIT_PHRASES = (
        "goodbye",
        "goodbye jarvis",
        "bye",
        "bye jarvis",
        "exit",
        "quit",
        "stop",
        "shutdown",
    )

    CALCULATION_START_WORDS = ( 
        "calculate", 
        "compute", 
        "solve", 
        "add", 
        "subtract", 
        "minus", 
        "multiply", 
        "times", 
        "divide", 
    )

    @classmethod
    def parse (cls, text: str) -> Command:
        """
        Parse raw speech text into a Command.
        
        Args:
            text:
                Raw text returned by speech recognition.
            
        Returns:
            A structured Command object.
        """

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
            return Command (
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
    def _normalize(text: str) ->  str:
        """
        Normalize user speech fro easier matching.
        """

        text = text.strip().lower()

         # Remove punctuation while preserving spaces.
        text = re.sub(
            r"[^\w\s]",
            "",
            text,
        )

        return re.sub(
            r"\s+",
            " ",
            text,
        )

    @classmethod
    def _is_greeting(cls, text: str) -> bool:
        """
        Check whether the text is a greeting.
        """

        return any(
            text == word
            or text.startswith(f"{word} ")
            for word in cls.GREETING_WORDS
        )

    @classmethod
    def _is_time_request(cls, text: str) -> bool:
        """
        Check whether the user is asking for the time.
        """

        return any(
            phrase in text
            for phrase in cls.TIME_PHRASES
        )

    @classmethod
    def _is_calculation(cls, text: str) -> bool:
        """
        Check whether the text contains a basic calculation.
        """

        if any( 
            text == word 
            or text.startswith(f"{word} ") 
            for word in cls.CALCULATION_START_WORDS 
        ): 
            return True 
        # Also recognize natural spoken forms such as: 
        # # "2 plus 2" 
        # # "5 times 6" 
        # # "10 divided by 2" 
        # # "2 add 3" 
        # # "5 minus 2" 
        spoken_operator_pattern = r""" 
            \b 
            \d+(?:\.\d+)? 
            \s+ (plus|add|minus|subtract|times|multiply|divided\s+by|divide) 
            \s+ 
            (?:\d+(?:\.\d+)?) 
            \b 
        """

        return bool(
            re.search(
                spoken_operator_pattern,
                text,
                re.IGNORECASE | re.VERBOSE,
            )
        )

    @classmethod
    def _is_exit_request(
        cls,
        text: str,
    ) -> bool:
        """
        Check whether the user wants JARVIS to stop.
        """

        return any(
            text == phrase
            or text.startswith(f"{phrase} ")
            for phrase in cls.EXIT_PHRASES
        )
