"""
Tests for the JARVIS Runtime foundation (Phase 3 & 4).
"""

from pathlib import Path
from unittest.mock import MagicMock

from core.executor import CommandExecutor
from core.runtime import JarvisRuntime
from core.state import StateManager
from speech.exceptions import EmptyTranscriptionError, SpeechError
from speech.models import SpeechResult
from voice.exceptions import VoiceError
from voice.service import VoiceService


def test_runtime_process_command_success() -> None:
    """Test successful single command execution loop."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.return_value = SpeechResult(
        text="hello",
        language="en",
        audio_path=Path("audio.wav"),
    )

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "HELLO, SIR! How can I help you?"

    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )
    should_continue = runtime.process_command()

    assert should_continue is True
    mock_voice.record_and_transcribe.assert_called_once()
    mock_executor.execute.assert_called_once()


def test_runtime_process_command_exit() -> None:
    """Test exit command returns False to stop loop."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.return_value = SpeechResult(
        text="goodbye",
        language="en",
        audio_path=Path("audio.wav"),
    )

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye, Sir."

    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )
    should_continue = runtime.process_command()

    assert should_continue is False


def test_runtime_run_loop_handles_voice_and_speech_errors() -> None:
    """Test runtime run loop catches VoiceError and SpeechError and continues."""
    mock_voice = MagicMock(spec=VoiceService)
    # First call raises VoiceError, second call raises SpeechError, third returns exit command
    mock_voice.record_and_transcribe.side_effect = [
        VoiceError("Microphone error"),
        SpeechError("Transcription failed"),
        SpeechResult(text="exit", language="en", audio_path=Path("audio.wav")),
    ]

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye, Sir."

    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )

    # Should run through voice error, speech error, then exit gracefully
    runtime.run()

    assert mock_voice.select_microphone.called
    assert mock_voice.record_and_transcribe.call_count == 3


def test_runtime_run_keyboard_interrupt() -> None:
    """Test runtime handles KeyboardInterrupt gracefully."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.select_microphone.side_effect = KeyboardInterrupt

    mock_executor = MagicMock(spec=CommandExecutor)
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )
    runtime.run()

    mock_voice.select_microphone.assert_called_once()


def test_runtime_run_unexpected_fatal_exception() -> None:
    """Test runtime catches unexpected fatal exception and exits cleanly."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.side_effect = RuntimeError("Fatal hardware failure")

    mock_executor = MagicMock(spec=CommandExecutor)
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )
    runtime.run()

    mock_voice.select_microphone.assert_called_once()
    mock_voice.record_and_transcribe.assert_called_once()
    mock_executor.execute.assert_not_called()


def test_runtime_run_keyboard_interrupt_during_loop() -> None:
    """Test runtime handles KeyboardInterrupt during command loop gracefully."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.select_microphone.return_value = None
    mock_voice.record_and_transcribe.side_effect = KeyboardInterrupt

    mock_executor = MagicMock(spec=CommandExecutor)
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )
    runtime.run()

    mock_voice.select_microphone.assert_called_once()
    mock_voice.record_and_transcribe.assert_called_once()
    mock_executor.execute.assert_not_called()


def test_runtime_run_empty_transcription_recovery() -> None:
    """Test runtime catches EmptyTranscriptionError via SpeechError boundary and continues."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.side_effect = [
        EmptyTranscriptionError("Empty transcription"),
        SpeechResult(text="exit", language="en", audio_path=Path("audio.wav")),
    ]

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye, Sir."

    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )
    runtime.run()

    assert mock_voice.select_microphone.called
    assert mock_voice.record_and_transcribe.call_count == 2
    mock_executor.execute.assert_called_once()


def test_runtime_dependency_reuse() -> None:
    """Test runtime reuses the same injected voice and executor dependencies across loop iterations."""
    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.side_effect = [
        SpeechResult(text="hello", language="en", audio_path=Path("audio.wav")),
        SpeechResult(text="time", language="en", audio_path=Path("audio.wav")),
        SpeechResult(text="exit", language="en", audio_path=Path("audio.wav")),
    ]

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Response"

    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=StateManager(),
    )
    runtime.run()

    assert runtime._voice is mock_voice
    assert runtime._executor is mock_executor
    mock_voice.select_microphone.assert_called_once()
    assert mock_voice.record_and_transcribe.call_count == 3
    assert mock_executor.execute.call_count == 3
