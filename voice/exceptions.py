"""
Custom exceptions for the voice module.
"""


class VoiceError(Exception):
    """
    Base exception for all voice-related errors.
    """


class RecordingError(VoiceError):
    """
    Raised when recording fails.
    """


class DeviceNotFoundError(VoiceError):
    """
    Raised when no microphone is available.
    """


class InvalidDeviceError(VoiceError):
    """
    Raised when a saved microphone is no longer available.
    """