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
    vad_calibration_duration: float = 1.0
    vad_threshold_multiplier: float = 3.0

    # --------------------------
    # Calibration Stability (Phase 1D)
    # --------------------------

    # Percentile used to estimate the robust upper noise level during calibration.
    # P90 ignores the top ~10% of calibration frames, preventing isolated spikes
    # from dominating the threshold.
    vad_calibration_percentile: float = 90.0

    # Maximum number of calibration retries after a degenerate window.
    # 1 initial window + 2 retries = 3 windows maximum.
    vad_calibration_max_retries: int = 2

    # Duration for which newly opened microphone input is drained before initial calibration
    # to allow device/driver/noise-cancellation transient settling.
    vad_stream_settle_duration: float = 2.0
