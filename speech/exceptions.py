"""
Custom exceptions for the speech module.
"""


class SpeechError(Exception):
    """
    Base exception for all speech-related errors.
    """


class AudioValidationError(SpeechError):
    """
    Raised when recorded audio is invalid.
    """


class SpeechRecognitionError(SpeechError):
    """
    Raised when speech recognition fails.
    """


class ModelLoadError(SpeechError):
    """
    Raised when the Whisper model cannot be loaded.
    """


class EmptyTranscriptionError(SpeechError):
    """
    Raised when speech recognition returns an empty or whitespace-only transcription.
    """
