"""
Voice Activity Detection (VAD).

This module detects whether an audio frame contains speech by measuring its RMS (Root Mean Square) energy.

The detector is intentionally independent of the recorder so it can be reused later for:
- Wake-word detection
- Continuous listening
- Streaming transcription
- Conversation made
"""


from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class VADConfig:
    """
    Configuration for Voice Activity Detection (VAD).
    """

    #Initial RMS threshold.
    energy_threshold: float = 0.015

    #Number of consecutive speech frames required.
    speech_frames: int = 3

    #number of consecutive silent frames required.
    silence_frames: int = 20

class VoiceActivityDetector:
    """
    Detects whether incoming audio contains speech.
    """

    def __init__(
        self,
        config: VADConfig | None = None,
    ) -> None:

        self.config = config or VADConfig()

        self._speech_counter = 0
        self._silence_counter = 0

        self._noise_floor = 0.0
        self._calibrated = False

    @property
    def noise_floor(self) -> float:
        """
        Current estimated room noise.
        """

        return self._noise_floor

    @property
    def calibrated(self) -> bool:
        """
        Whether calibration has completed.
        """

        return self._calibrated

    @staticmethod
    def rms(
        audio: np.ndarray,
    ) -> float:
        """
        Calculate RMS energy of an audio frame.
        """

        if audio.size == 0:
            return 0.0

        return float(
            np.sqrt(
                np.mean(
                    np.square(audio)
                )
            )
        )

    def is_speech(
            self,
            audio: np.ndarray,
    ) -> bool:
        """
        Return True if the frame contains speech.
        """

        energy = self.rms(audio)

        return energy >= self.config.energy_threshold

    def process(
            self,
            audio: np.ndarray,
    ) -> tuple[bool, float]:
        """
        Process one frame of audio.
        
        Returns:
            (speech_detected, rms_energy)
        """

        energy = self.rms(audio)

        if energy >= self.config.energy_threshold:

            self._speech_counter += 1
            self._silence_counter = 0

        else:
            self._silence_counter += 1
            self._speech_counter = 0

        speech_detected = (
            self._speech_counter >= self.config.speech_frames
        )

        return speech_detected, energy

    def reset(self) -> None:
        """
        Reset speech and silence counters.
        """

        self._speech_counter = 0
        self._silence_counter = 0

    
    def calibrate(
        self,
        samples: list[np.ndarray],
        threshold_multiplier: float = 3.0,
    ) -> None:
        """
        Learn the background noise level and adjust
        the speech detection threshold.
        """

        if not samples:
            return

        energies = np.array([
            self.rms(frame)
            for frame in samples
        ])

        self._noise_floor = float(
            np.median(energies)
        )

        noise_std = float(
            np.std(energies)
        )

        self.config.energy_threshold = max(
            self._noise_floor
            + (threshold_multiplier * noise_std),
            0.01,
        )

        self._calibrated = True

    @property
    def silence_detected(self) -> bool:
        """
        Return True if enough consecutive silent frames have been detected.
        """

        return (
            self._silence_counter
            >= self.config.silence_frames
        )    