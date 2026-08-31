"""Tests for Phase 1B/1D voice recorder reliability."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voice.config import VoiceConfig
from voice.exceptions import RecordingError
from voice.recorder import VoiceRecorder
from voice.vad import VoiceActivityDetector


def test_vad_calibration_persists_after_reset():
    """Calibration state survives reset(); only counters are cleared."""

    vad = VoiceActivityDetector()

    # Deterministic samples (constant low energy noise)
    samples = [np.full((160, 1), 0.02) for _ in range(10)]
    threshold, noise_floor, _ = vad.analyze_calibration(samples)
    vad.apply_calibration(threshold, noise_floor)

    assert vad.calibrated is True
    original_threshold = vad.config.energy_threshold

    # Drive VAD through normal processing to change transient state
    vad.process(np.full((160, 1), 0.1)) # Speech
    vad.process(np.full((160, 1), 0.0)) # Silence

    assert vad._speech_counter == 0
    assert vad._silence_counter == 1

    vad.reset()

    assert vad.calibrated is True
    assert vad.config.energy_threshold == original_threshold
    assert vad._speech_counter == 0
    assert vad._silence_counter == 0


@patch('voice.recorder.VoiceRecorder._calibrate')
@patch('voice.recorder.VoiceRecorder._read_frame')
def test_recorder_skips_recalibration_when_calibrated(
        mock_read,
        mock_calibrate,
):
    """Recorder does not recalibrate when the VAD is already calibrated."""

    recorder = VoiceRecorder(VoiceConfig())

    # Bring the VAD into a calibrated state through its public API.
    recorder.vad.apply_calibration(0.028, 0.02)
    assert recorder.vad.calibrated is True

    mock_read.side_effect = Exception("Break loop")

    mock_stream = MagicMock()
    mock_stream.__enter__.return_value = mock_stream

    with patch.object(recorder, '_create_stream', return_value=mock_stream), pytest.raises(Exception, match="Break loop"):
        recorder._collect_audio()

    mock_calibrate.assert_not_called()


@patch('voice.recorder.time.monotonic')
@patch('voice.recorder.VoiceRecorder._calibrate')
@patch('voice.recorder.VoiceRecorder._read_frame')
def test_speech_start_timeout_starts_after_calibration(
        mock_read,
        mock_calibrate,
        mock_time,
):
    """The speech-start timeout clock begins after calibration, not before."""

    call_order = []

    def record_event(name):
        call_order.append(name)
        return 10.0 + len(call_order) # Incrementing time

    # Mock calibration to record when it happened (settle does not call calibrate)
    def mocked_calibrate(stream):
        record_event("calibrate")

    mock_calibrate.side_effect = mocked_calibrate

    # Mock time.monotonic to record when it was called for timeout check
    mock_time.side_effect = lambda: record_event("time") or (10.0 + len(call_order))

    recorder = VoiceRecorder(
        VoiceConfig(speech_start_timeout=3.0)
    )

    with patch.object(recorder, '_create_stream'), \
         patch.object(recorder, '_settle_stream'), \
         patch.object(recorder.vad, 'process', return_value=(False, 0.0)), \
         pytest.raises(RecordingError):
        recorder._collect_audio()

    # Verify order: calibrate must appear before the first time check for timeout
    assert "calibrate" in call_order
    assert "time" in call_order

    calibrate_index = call_order.index("calibrate")
    time_index = call_order.index("time")

    assert calibrate_index < time_index


@patch('voice.recorder.time.monotonic', side_effect=[0.0, 0.5, 1.5])
@patch('voice.recorder.VoiceRecorder._read_frame')
def test_recorder_good_first_window(mock_read, mock_time):
    """Good first window: one analysis attempt, calibration applied, no retry."""
    mock_read.return_value = np.full(
        (160, 1),
        0.01,
        dtype=np.float32,
    )
    config = VoiceConfig(vad_calibration_max_retries=2, vad_calibration_duration=1.0)
    recorder = VoiceRecorder(config)

    # Mock analyze_calibration to return valid result on first call
    recorder.vad.analyze_calibration = MagicMock(return_value=(0.02, 0.01, False))
    # We must patch the ACTUAL apply_calibration method
    with patch.object(recorder.vad, 'apply_calibration', wraps=recorder.vad.apply_calibration) as mock_apply:
        recorder._calibrate(MagicMock())

        assert recorder.vad.analyze_calibration.call_count == 1
        assert mock_apply.call_count == 1
        assert recorder.vad.calibrated is True


@patch(
    'voice.recorder.time.monotonic',
    side_effect=[
        0.0, 0.5, 1.5,
        2.0, 2.5, 3.5,
        4.0, 4.5, 5.5,
    ],
)
@patch('voice.recorder.VoiceRecorder._read_frame')
def test_recorder_retry_success(mock_read, mock_time):
    """Degenerate then valid: exactly 3 attempts (1 initial + 2 retries), calibrated=True."""
    mock_read.return_value = np.full(
        (160, 1),
        0.01,
        dtype=np.float32,
    )
    config = VoiceConfig(vad_calibration_max_retries=2, vad_calibration_duration=1.0)
    recorder = VoiceRecorder(config)

    # Mock analyze_calibration: first two degenerate, third valid
    recorder.vad.analyze_calibration = MagicMock(side_effect=[
        (0.0, 0.0, True),   # Attempt 0: degenerate
        (0.0, 0.0, True),   # Attempt 1: degenerate
        (0.03, 0.01, False), # Attempt 2: valid
    ])
    # We must patch the ACTUAL apply_calibration method
    with patch.object(recorder.vad, 'apply_calibration', wraps=recorder.vad.apply_calibration) as mock_apply:
        recorder._calibrate(MagicMock())

        assert recorder.vad.analyze_calibration.call_count == 3
        assert mock_apply.call_count == 1
        assert recorder.vad.calibrated is True
        assert recorder.vad.config.energy_threshold == 0.03
        assert recorder.vad.noise_floor == 0.01


@patch(
    'voice.recorder.time.monotonic',
    side_effect=[
        0.0, 0.5, 1.5,
        2.0, 2.5, 3.5,
        4.0, 4.5, 5.5,
    ],
)
@patch('voice.recorder.VoiceRecorder._read_frame')
def test_recorder_three_degenerate_failures(mock_read, mock_time):
    """Three degenerate attempts: RecordingError, apply_calibration never called, calibrated=False."""
    mock_read.return_value = np.full(
        (160, 1),
        0.01,
        dtype=np.float32,
    )
    config = VoiceConfig(vad_calibration_max_retries=2, vad_calibration_duration=1.0)
    recorder = VoiceRecorder(config)

    # Mock analyze_calibration to always return degenerate
    recorder.vad.analyze_calibration = MagicMock(return_value=(0.0, 0.0, True))
    with patch.object(recorder.vad, 'apply_calibration', wraps=recorder.vad.apply_calibration) as mock_apply:

        with pytest.raises(RecordingError, match="Calibration failed"):
            recorder._calibrate(MagicMock())

        assert recorder.vad.analyze_calibration.call_count == 3
        assert mock_apply.call_count == 0
        assert recorder.vad.calibrated is False
        assert recorder.vad.config.energy_threshold == 0.008  # unchanged base


@patch('voice.recorder.time.monotonic', side_effect=[0.0, 0.5, 1.5, 2.5])
@patch('voice.recorder.VoiceRecorder._read_frame')
def test_settle_stream_drains_frames(mock_read, mock_time):
    """_settle_stream calls _read_frame until duration elapses."""
    mock_read.return_value = np.full((160, 1), 0.01, dtype=np.float32)
    recorder = VoiceRecorder(VoiceConfig(vad_stream_settle_duration=1.0))
    stream = MagicMock()
    recorder._settle_stream(stream)
    # At 0.0 start; 0.5 true; 1.5 false -> one call
    assert mock_read.call_count == 1


@patch('voice.recorder.VoiceRecorder._settle_stream')
@patch('voice.recorder.VoiceRecorder._calibrate')
@patch('voice.recorder.VoiceRecorder._read_frame')
@patch('voice.recorder.time.monotonic', side_effect=[0.0, 0.5])
def test_uncalibrated_vad_settle_then_calibrate(mock_time, mock_read, mock_calibrate, mock_settle):
    """Uncalibrated VAD: settle then calibrate then listen."""
    call_order = []
    mock_settle.side_effect = lambda stream: call_order.append("settle")
    mock_calibrate.side_effect = lambda stream: call_order.append("calibrate")

    recorder = VoiceRecorder(VoiceConfig())
    # Ensure uncalibrated state for settle-then-calibrate test
    recorder.vad._calibrated = False
    with patch.object(recorder, '_create_stream', return_value=MagicMock()):
        # Break out of loop immediately
        mock_read.side_effect = Exception("stop")
        with pytest.raises(Exception, match="stop"):
            recorder._collect_audio()

    assert call_order == ["settle", "calibrate"]
    mock_settle.assert_called_once()
    mock_calibrate.assert_called_once()


@patch('voice.recorder.VoiceRecorder._settle_stream')
@patch('voice.recorder.VoiceRecorder._calibrate')
@patch('voice.recorder.VoiceRecorder._read_frame')
@patch('voice.recorder.time.monotonic', side_effect=[0.0, 0.5])
def test_calibrated_vad_skips_settle_and_calibrate(mock_time, mock_read, mock_calibrate, mock_settle):
    """Calibrated VAD does not settle or calibrate."""
    recorder = VoiceRecorder(VoiceConfig())
    recorder.vad.apply_calibration(0.02, 0.01)
    with patch.object(recorder, '_create_stream', return_value=MagicMock()):
        mock_read.side_effect = Exception("stop")
        with pytest.raises(Exception, match="stop"):
            recorder._collect_audio()
    mock_settle.assert_not_called()
    mock_calibrate.assert_not_called()


@patch('voice.recorder.time.monotonic', return_value=0.0)
@patch('voice.recorder.VoiceRecorder._read_frame')
def test_settle_stream_zero_duration(mock_read, mock_time):
    """Zero settle duration means no reads."""
    recorder = VoiceRecorder(VoiceConfig(vad_stream_settle_duration=0.0))
    recorder._settle_stream(MagicMock())
    mock_read.assert_not_called()
