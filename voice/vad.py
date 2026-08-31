"""
Voice Activity Detection (VAD).

This module detects whether an audio frame contains speech by measuring its RMS (Root Mean Square) energy.

The detector is intentionally independent of the recorder so it can be reused later for:
- Wake-word detection
- Continuous listening
- Streaming transcription
- Conversation mode
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class VADConfig:
    """
    Configuration for Voice Activity Detection (VAD).
    """

    # Initial RMS threshold.
    energy_threshold: float = 0.015

    # Number of consecutive speech frames required.
    speech_frames: int = 3

    # Number of consecutive silent frames required.
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

        # Preserved base threshold for robust calibration analysis.
        self._base_energy_threshold = self.config.energy_threshold

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

    @property
    def base_energy_threshold(self) -> float:
        """
        Base energy threshold configured at startup.
        """
        return self._base_energy_threshold

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
        above_threshold = energy >= self.config.energy_threshold

        # 1. Update counters FIRST
        if above_threshold:
            self._speech_counter += 1
            self._silence_counter = 0
        else:
            self._silence_counter += 1
            self._speech_counter = 0

        # 2. THEN update speech_detected
        speech_detected = self._speech_counter >= self.config.speech_frames

        return speech_detected, energy

    def reset(self) -> None:
        """
        Reset speech and silence counters.
        """

        self._speech_counter = 0
        self._silence_counter = 0

    def analyze_calibration(
        self,
        samples: list[np.ndarray],
        percentile: float = 90.0,
    ) -> tuple[float, float, bool]:
        """
        Analyze calibration samples using robust statistics.

        Returns:
            (threshold, noise_floor_estimate, is_degenerate)
        """
        if not samples:
            return self.config.energy_threshold, 0.0, True

        energies = np.array([self.rms(frame) for frame in samples])
        noise_floor = float(np.median(energies))
        noise_ceiling = float(np.percentile(energies, percentile))

        # Degenerate: microphone is effectively silent (lower than base noise threshold)
        is_degenerate = noise_ceiling < self._base_energy_threshold

        if is_degenerate:
            return 0.0, noise_floor, True

        # Formula: threshold = noise_ceiling + base_threshold
        threshold = noise_ceiling + self._base_energy_threshold
        return threshold, noise_floor, False

    def apply_calibration(self, threshold: float, noise_floor: float) -> None:
        """Store accepted calibration state."""
        self.config.energy_threshold = threshold
        self._noise_floor = noise_floor
        self._calibrated = True

    def calibrate(
        self,
        samples: list[np.ndarray],
        threshold_multiplier: float = 3.0,
    ) -> None:
        """
        Wrapper for legacy API compatibility.

        The `threshold_multiplier` parameter is ignored.
        Calibration uses the robust P90 + base_threshold formula
        implemented in analyze_calibration().
        """
        threshold, noise_floor, is_degenerate = self.analyze_calibration(samples)
        if not is_degenerate:
            self.apply_calibration(threshold, noise_floor)

    @property
    def silence_detected(self) -> bool:
        """
        Return True if enough consecutive silent frames have been detected.
        """

        return (
            self._silence_counter
            >= self.config.silence_frames
        )
