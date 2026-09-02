"""
Tests for the JARVIS Central State Manager (Phase 4).
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.executor import CommandExecutor
from core.runtime import JarvisRuntime
from core.state import InvalidStateTransitionError, JarvisState, StateManager
from speech.exceptions import SpeechError
from speech.models import SpeechResult
from voice.exceptions import VoiceError
from voice.service import VoiceService


def test_state_manager_initial_state() -> None:
    """Test state manager starts in OFFLINE state by default or specified state."""
    sm = StateManager()
    assert sm.current_state == JarvisState.OFFLINE

    sm_idle = StateManager(initial_state=JarvisState.IDLE)
    assert sm_idle.current_state == JarvisState.IDLE


def test_state_manager_valid_transition() -> None:
    """Test valid state transitions succeed."""
    sm = StateManager(initial_state=JarvisState.OFFLINE)
    sm.transition(JarvisState.INITIALIZING)
    assert sm.current_state == JarvisState.INITIALIZING

    sm.transition(JarvisState.IDLE)
    assert sm.current_state == JarvisState.IDLE

    sm.transition(JarvisState.LISTENING)
    assert sm.current_state == JarvisState.LISTENING


def test_state_manager_invalid_transition() -> None:
    """Test invalid state transitions raise InvalidStateTransitionError."""
    sm = StateManager(initial_state=JarvisState.OFFLINE)
    with pytest.raises(InvalidStateTransitionError):
        sm.transition(JarvisState.EXECUTING)


def test_state_manager_offline_and_error_universal_escape() -> None:
    """Test any state can transition to OFFLINE or ERROR."""
    sm = StateManager(initial_state=JarvisState.LISTENING)
    sm.transition(JarvisState.ERROR)
    assert sm.current_state == JarvisState.ERROR

    sm.transition(JarvisState.OFFLINE)
    assert sm.current_state == JarvisState.OFFLINE


def test_runtime_startup_and_success_lifecycle() -> None:
    """Test runtime startup and successful command lifecycle state transitions."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.return_value = SpeechResult(
        text="exit",
        language="en",
        audio_path=Path("audio.wav"),
    )

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye, Sir."

    state_manager = StateManager()
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=state_manager,
    )

    assert runtime.current_state == JarvisState.OFFLINE

    runtime.run()

    assert runtime.current_state == JarvisState.OFFLINE
    mock_voice.select_microphone.assert_called_once()
    mock_voice.record_and_transcribe.assert_called_once()


def test_runtime_voice_error_lifecycle() -> None:
    """Test runtime handles recoverable VoiceError and returns to IDLE."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.side_effect = [
        VoiceError("Mic disconnected"),
        SpeechResult(text="exit", language="en", audio_path=Path("audio.wav")),
    ]

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye, Sir."

    state_manager = StateManager()
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=state_manager,
    )

    runtime.run()
    assert runtime.current_state == JarvisState.OFFLINE


def test_runtime_speech_error_lifecycle() -> None:
    """Test runtime handles recoverable SpeechError and returns to IDLE."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.side_effect = [
        SpeechError("Transcription failed"),
        SpeechResult(text="exit", language="en", audio_path=Path("audio.wav")),
    ]

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye, Sir."

    state_manager = StateManager()
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=state_manager,
    )

    runtime.run()
    assert runtime.current_state == JarvisState.OFFLINE


def test_runtime_fatal_exception_lifecycle() -> None:
    """Test runtime handles unexpected fatal exception and shuts down cleanly."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.side_effect = RuntimeError("Fatal crash")

    mock_executor = MagicMock(spec=CommandExecutor)

    state_manager = StateManager()
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=state_manager,
    )

    runtime.run()
    assert runtime.current_state == JarvisState.OFFLINE


def test_runtime_keyboard_interrupt_lifecycle() -> None:
    """Test runtime handles KeyboardInterrupt gracefully and shuts down cleanly."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.select_microphone.side_effect = KeyboardInterrupt

    mock_executor = MagicMock(spec=CommandExecutor)

    state_manager = StateManager()
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=state_manager,
    )

    runtime.run()
    assert runtime.current_state == JarvisState.OFFLINE


def test_runtime_dependency_reuse() -> None:
    """Test runtime reuses injected dependencies and state manager."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.return_value = SpeechResult(
        text="exit",
        language="en",
        audio_path=Path("audio.wav"),
    )
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye"
    state_manager = StateManager()

    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=state_manager,
    )

    runtime.run()

    assert runtime.state_manager is state_manager
    assert runtime._voice is mock_voice
    assert runtime._executor is mock_executor
