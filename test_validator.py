from pathlib import Path

from speech.validator import AudioValidator

AudioValidator.validate(
    Path("recordings/does_not_exist.wav")
)