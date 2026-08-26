"""
Command execution layer for JARVIS.

This module takes a parsed command snd executes the corresponding action.
"""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from core.calculator import calculate
from core.commands import Command, CommandType


class CommandExecutor:
    """
    Executes commands produced by the command parser.
    """

    def execute(
            self,
            command: Command,
        ) -> str:
        """
        Execute a parsed command.
        
        Args:
            command:
                Parsed command produced by CommandParser.
        
        Returns:
            Response generatted by JARVIS.
        """

        if command.command_type is CommandType.GREETING:
          return "HELLO, SIR! How can I help you?"

        if command.command_type is CommandType.GET_TIME:
            return self._get_time()

        if command.command_type is CommandType.CALCULATE:
            return self._calculate(command.text)

        if command.command_type is CommandType.EXIT:
            return "Goodbye, Sir."

        return "Sorry, I don't understand that command."

    @staticmethod
    def _get_time() -> str:
        """
        Return the current local time.
        """

        current_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
            ).strftime("%I:%M %p")

        return f"The current time is {current_time}."

    @staticmethod
    def _calculate(text: str) -> str:
        """
        Execute a basic arithmetic calculation.

        Supports natural spoken arithmetic such as: 
            calculate 2 plus 2, 
            calculate 2 add 2, 
            add 2 and 3,
            subtract 5 from 10, 
            multiply 6 by 7,
            divide 20 by 4
        """

        expression = text.strip()

        expression = CommandExecutor._normalize_spoken_math(
            expression 
        )

        if not expression:
            return "I could not find a calculation to perform."

        try:
            result = calculate(expression)

        except ZeroDivisionError:
            return "I cannot divide by zero."

        except ValueError:
            return "I could not understand that calculation."

        return f"The answer is {result}."

    @staticmethod 
    def _normalize_spoken_math(text: str) -> str: 
        """ 
        Convert spoken arithmetic into symbolic arithmetic expression. """ 

        text = text.lower().strip() 

        # Remove common calculation command prefixes.  
        text = re.sub( 
            r"^\s*(calculate|compute|solve)\s+", 
            "", 
            text, 
        )

        # ------------------------------------------------- 
        # Natural sentence patterns 
        # ------------------------------------------------- 
        # "add 2 and 3" -> "2 + 3" 
        match = re.fullmatch( 
            r"add\s+(-?\d+(?:\.\d+)?)\s+and\s+(-?\d+(?:\.\d+)?)", 
            text, 
            ) 

        if match: 
            left, right = match.groups() 
            return f"{left} + {right}" 

        # "subtract 5 from 10" -> "10 - 5" 
        match = re.fullmatch( 
            r"subtract\s+(-?\d+(?:\.\d+)?)\s+from\s+(-?\d+(?:\.\d+)?)", 
            text, 
        ) 

        if match: 
            amount, original = match.groups() 
            return f"{original} - {amount}" 

        # "multiply 6 by 7" -> "6 * 7" 
        match = re.fullmatch( 
            r"multiply\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)", 
            text, 
        ) 

        if match: 
            left, right = match.groups() 
            return f"{left} * {right}" 

        # "divide 20 by 4" -> "20 / 4" 
        match = re.fullmatch( 
            r"divide\s+(-?\d+(?:\.\d+)?)\s+by\s+(-?\d+(?:\.\d+)?)", 
            text, 
        ) 

        if match: 
            left, right = match.groups() 
            return f"{left} / {right}" 

        # ------------------------------------------------- 
        # Spoken operator patterns 
        # -------------------------------------------------

        # Longer phrases must be replaced first. 
        replacements = ( 
            (r"\bdivided\s+by\b", "/"), 
            (r"\bmultiply\s+by\b", "*"), 
            (r"\bmultiplied\s+by\b", "*"), 
            (r"\bplus\b", "+"), 
            (r"\badd\b", "+"), 
            (r"\bminus\b", "-"), 
            (r"\bsubtract\b", "-"), 
            (r"\btimes\b", "*"), 
            (r"\bmultiply\b", "*"), 
            (r"\bdivide\b", "/"), 
        ) 

        for pattern, replacement in replacements: 
            text = re.sub( 
                pattern, 
                f" {replacement} ", 
                text, 
            )

        # Remove filler word "and". 
        text = re.sub( 
            r"\band\b", 
            " ", 
            text, 
        ) 

        # Keep only the expression characters. 
        text = re.sub( 
            r"[^0-9+\-*/.\s]", 
            " ", 
            text, 
        ) 

        return re.sub( 
            r"\s+", 
            " ", 
            text, 
        ).strip()