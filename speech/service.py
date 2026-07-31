"""
High-level speech service.
"""

from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)
from speech.config import SpeechConfig
from speech.models import SpeechResult
from speech.validator import AudioValidator
from speech.whisper import FasterWhisperRecognizer


class SpeechService:
    """
    Coordinates speech recognition.
    """

    def __init__(
            self,
            config: SpeechConfig | None = None,
    ) -> None:
        self.config = config or SpeechConfig()

        self.recognizer = FasterWhisperRecognizer(
            self.config
        )

    def transcribe(
            self,
            audio_path: Path,
    ) -> SpeechResult:
        """
        Convert an audio file into text.
        """
        logger.info(
            "Validating recorded audio..."
        )

        AudioValidator.validate(audio_path)

        logger.info(
            "Audio validation successful."
        )   

        logger.info(
            "Starting speech recognition..."
        )
        
        result = self.recognizer.transcribe(audio_path)

        logger.info(
            "Speech recognition completed."
        )

        return result
