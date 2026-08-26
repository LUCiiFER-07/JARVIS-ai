"""
Audio validation utilities.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import numpy as np
import soundfile as sf

from speech.exceptions import AudioValidationError


class AudioValidator:
    """
    Validates recorded audio before speech recognition.
    """

    #Minimum accepted recording duration (seconds)
    MIN_DURATION: ClassVar[float] = 0.5

    #Reject recordings smaller than this.
    MIN_FILE_SIZE: ClassVar[int] = 1024 # 1 KB

    #Minimum RMS energy.
    MIN_RMS: ClassVar[float] = 0.003

    @classmethod
    def validate(
        cls,
        audio_path: Path,
    ) -> None:
        """
        Validate an audio recording.
        
        Raises:
            AudioValidationError:
                If the recording fails validation.
        """

        cls._check_exists(audio_path)
        cls._check_size(audio_path)

        audio, sample_rate = sf.read(audio_path)

        cls._check_not_empty(audio)
        cls._check_duration(audio, sample_rate)
        cls._check_energy(audio)

    @staticmethod
    def _check_exists(audio_path: Path) -> None:
        """Ensure the recording exists."""

        if not audio_path.exists():
            raise AudioValidationError(
                f"Recording not found:\n{audio_path}"
            )

    @classmethod
    def _check_size(
        cls,
        audio_path: Path,
    ) -> None:
        """Ensure the file is not empty."""

        size = audio_path.stat().st_size

        if size < cls.MIN_FILE_SIZE:
            raise AudioValidationError(
                "Recording is too small."
            )

    @staticmethod
    def _check_not_empty(
        audio: np.ndarray,
    ) -> None:
        """Ensure samples exist."""

        if audio.size == 0:
            raise AudioValidationError(
                "Recording contains no audio."
            )

    @classmethod
    def _check_duration(
        cls,
        audio: np.ndarray,
        sample_rate: int,
    ) -> None:
        """Ensure recording is long enough."""

        duration = len(audio) / sample_rate

        if duration < cls.MIN_DURATION:
            raise AudioValidationError(
                "Recording is too short."
            )

    @classmethod
    def _check_energy(
        cls,
        audio: np.ndarray,
    ) -> None:
        """
        Ensure recording contains enough energy.
        """

        rms = np.sqrt(
            np.mean(
                np.square(audio)
            )
        )

        if rms < cls.MIN_RMS:
            raise AudioValidationError(
                "No speech detected."
            )