"""
Speech recognition models.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SpeechResult:
    """Represents the result of speech recongnition.
    """

    text: str
    language: str
    audio_path: Path