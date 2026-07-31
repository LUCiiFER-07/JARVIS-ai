"""
Configuration for speech recognition.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class SpeechConfig:
    """
    Speech recognition configuration.
    """
    # Whisper model.
    model_name: str ="small"

    # Language hint.
    language: str = "en"

    # Decoding beam size.
    beam_size: int = 3

    # CPU optimization.
    compute_type: str = "int8"

    # CPU by default.
    device: str = "cpu"