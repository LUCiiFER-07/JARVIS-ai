"""
Speech recognizer interface.
"""

from pathlib import Path
from typing import Protocol

from speech.models import SpeechResult


class SpeechRecognizer(Protocol):
    """
    Protocol for speech recognition engines.
    """

    def transcribe(
            self,
            audio_path: Path,
    ) -> SpeechResult:
        """
        Convert speech to text.
        
        Args:
            audio_path: Path to the audio file.
        
        Returns:
            Speech recognition result.
        """
