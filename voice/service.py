"""
High -level interface for the voice module.
"""

from pathlib import Path

from speech.models import SpeechResult
from speech.service import SpeechService
from utils.logger import get_logger
from voice.config import VoiceConfig
from voice.manager import DeviceManager
from voice.recorder import VoiceRecorder

logger = get_logger(__name__)


class VoiceService:
    """
    High-level interface for the voice operations.
    
    This class coordinates microphone selection and audio recording while hiding the implementation details of the underlying voice components.
    """

    def __init__(
        self,
        config: VoiceConfig | None = None,
        speech_service: SpeechService | None = None,
    ) -> None:
        """
        Initialise the voice service.
        
        Args:
            config: Optiona; voice configuration.
        """

        self.speech = speech_service or SpeechService()

        self.config = config or VoiceConfig()

        self.recorder = VoiceRecorder(self.config)

    def select_microphone(self) -> None:
        """
        Let the user select the microphone to use.
        """
        #Ask the user to choose a microphone.
        microphone = DeviceManager.get_microphone()

        #Save microphone index.
        self.config.device = microphone.index

        #Use the microphone's preferred sample rate.
        self.config.sample_rate = microphone.sample_rate

        logger.info(
            "Selected microphone: %s | Device=%d | Sample Rate=%d Hz",
            microphone.name,
            microphone.index,
            microphone.sample_rate,
)

    def record(
        self,
        filename: str = "recording.wav",
    ) -> Path:
        """
        Record audio using the selected microphone.
        
        Args:
            filename: Name of the output WAV file.
            
        Returns:
            Path to the recorded audio file.
        """

        return self.recorder.record(
            filename=filename,
        )

    def record_and_transcribe(
        self,
        filename: str = "my_voice.wav",
    ) -> SpeechResult:
        """
        Record speech from the microphone and transcribe it.

        Args:
            filename:
                Output audio filename.

        Returns:
            Speech recognition result.

        Raises:
            EmptyTranscriptionError: If transcription returns empty/whitespace-only text.
        """

        audio_path = self.record(filename)

        return self.speech.transcribe(audio_path)