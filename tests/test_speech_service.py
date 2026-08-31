"""Tests for Phase 1C: Empty transcription handling."""

from pathlib import Path
from unittest.mock import patch

import pytest

from speech.exceptions import EmptyTranscriptionError
from speech.models import SpeechResult
from speech.service import SpeechService
from speech.whisper import FasterWhisperRecognizer


@patch('speech.service.AudioValidator.validate')
@patch.object(FasterWhisperRecognizer, '__init__', lambda self, config=None: None)
@patch.object(FasterWhisperRecognizer, 'transcribe')
def test_transcribe_raises_on_empty_text(mock_transcribe, mock_validate):
    """SpeechService.transcribe raises EmptyTranscriptionError on empty text."""

    mock_transcribe.return_value = SpeechResult(
        text="",
        language="en",
        audio_path=Path("test.wav"),
    )

    service = SpeechService()

    with pytest.raises(EmptyTranscriptionError):
        service.transcribe(Path("test.wav"))


@patch('speech.service.AudioValidator.validate')
@patch.object(FasterWhisperRecognizer, '__init__', lambda self, config=None: None)
@patch.object(FasterWhisperRecognizer, 'transcribe')
def test_transcribe_raises_on_whitespace_only(mock_transcribe, mock_validate):
    """SpeechService.transcribe raises EmptyTranscriptionError on whitespace-only text."""

    mock_transcribe.return_value = SpeechResult(
        text="   \n\t  ",
        language="en",
        audio_path=Path("test.wav"),
    )

    service = SpeechService()

    with pytest.raises(EmptyTranscriptionError):
        service.transcribe(Path("test.wav"))


@patch('speech.service.AudioValidator.validate')
@patch.object(FasterWhisperRecognizer, '__init__', lambda self, config=None: None)
@patch.object(FasterWhisperRecognizer, 'transcribe')
def test_transcribe_succeeds_on_valid_text(mock_transcribe, mock_validate):
    """SpeechService.transcribe returns result on valid non-empty text."""

    mock_transcribe.return_value = SpeechResult(
        text="hello jarvis",
        language="en",
        audio_path=Path("test.wav"),
    )

    service = SpeechService()
    result = service.transcribe(Path("test.wav"))

    assert result.text == "hello jarvis"
    assert result.language == "en"