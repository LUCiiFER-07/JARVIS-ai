"""
Represents an audio input device.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AudioDevice:
    """
    Represents one microphone device.
    """

    index: int
    name: str
    channels: int

    #Default sample rate supported by this microphone.
    sample_rate: int