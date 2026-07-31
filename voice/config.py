"""
Configuration for the voice module.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class VoiceConfig:

    """
    Voice configuration.
    Stores all voice recording related settings.
    """

    sample_rate: int = 16_000
    channels: int = 1
    duration: int = 5
    device: int | None = None

    # --------------------------
    # Voice Activity Detection
    # --------------------------

    vad_energy_threshold: float = 0.008          # RMS energy threshold for detecting speech.
    vad_speech_frames: int = 5                  # Number of consecutive speech frames required.
    vad_silence_frames: int = 30                # Number of consecutive silent frames before stopping.
    vad_frame_duration_ms: int = 30             # Frame duration (milliseconds).
    max_recording_duration: float = 20.0        # Maximum recording duration (seconds).
    speech_start_timeout: float = 10.0         # Timeout for detecting the start of a voice command
    pre_roll_frames: int = 10                   # Number of frames to keep before speech starts.
