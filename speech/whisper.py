"""
Faster-Whisper speech recognizer.
"""

from pathlib import Path

from faster_whisper import WhisperModel

from speech.config import SpeechConfig
from speech.exceptions import ModelLoadError, SpeechRecognitionError
from speech.models import SpeechResult
from speech.recognizer import SpeechRecognizer
from utils.logger import get_logger

logger = get_logger(__name__)

class FasterWhisperRecognizer(SpeechRecognizer):
    """
    Faster-Whisper implementation of SpeechRecognizer.
    """

    def __init__(
            self,
            config: SpeechConfig | None =  None,
    ) -> None:
        """
        Initialize the Whisper model.
        """

        self.config = config or SpeechConfig()

        logger.info(
            "Loading Whisper model: %s",
            self.config.model_name,
        )

        try:
            self.model = WhisperModel(
                model_size_or_path=self.config.model_name,
                device=self.config.device,
                compute_type=self.config.compute_type,
            )

        except Exception as error:
            logger.exception(
                "Failed to load Whisper model."
            )
            raise ModelLoadError(
                "Failed to load Whisper model."
            ) from error

        logger.info(
            "Whisper model loaded successfully."
        )

    def transcribe(
            self,
            audio_path: Path,
    ) -> SpeechResult:
        """
        Convert speech to text.

        Args:
            audio_path: Path to the WAV file.

        Returns:
            Speech recognition result.
        """

        logger.info(
            "Starting Whisper transcription: %s",
            audio_path,
        )

        try:
            segments, info = self.model.transcribe(
                str(audio_path),
                language=self.config.language,
                beam_size=self.config.beam_size,
            )

        except Exception as error:
            logger.exception(
                "Speech recognition failed."
            )
            raise SpeechRecognitionError(
                "Speech recognition failed."
            ) from error
        
        segments = list(segments)

        logger.debug(
            "Whisper detected %d segments.", 
            len(segments),
        )

        for segment in segments:
            logger.debug(
                "%.2fs -> %.2fs | %s",
                segment.start,
                segment.end,
                segment.text,
            )
        
        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        return SpeechResult(
            text=text,
            language=info.language,
            audio_path=audio_path,
        )
