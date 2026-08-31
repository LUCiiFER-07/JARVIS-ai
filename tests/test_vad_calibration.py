"""Deterministic unit tests for VAD calibration (Phase 1D)."""

import numpy as np

from voice.vad import VADConfig, VoiceActivityDetector


def test_process_speech_frame_boundary():
    """Exact speech frame boundary with speech_frames=5.

    5 consecutive above-threshold frames required.
    """
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.01, speech_frames=5))

    # 4 consecutive above-threshold frames
    assert vad.process(np.full((160, 1), 0.1))[0] is False
    assert vad.process(np.full((160, 1), 0.1))[0] is False
    assert vad.process(np.full((160, 1), 0.1))[0] is False
    assert vad.process(np.full((160, 1), 0.1))[0] is False

    # 5th consecutive above-threshold frame -> speech_detected becomes True
    assert vad.process(np.full((160, 1), 0.1))[0] is True


def test_process_first_silent_frame_after_speech():
    """First below-threshold frame after speech detection returns False, silence_detected False."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.01, speech_frames=2, silence_frames=3))

    # Get speech detected
    vad.process(np.full((160, 1), 0.1))
    vad.process(np.full((160, 1), 0.1))  # speech_detected = True

    # First silent frame
    assert vad.process(np.full((160, 1), 0.005))[0] is False
    assert vad.silence_detected is False


def test_process_exact_silence_boundary():
    """Exact silence boundary with silence_frames=30.

    Silent frames 1-29: silence_detected=False
    Silent frame 30: silence_detected=True
    """
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.01, speech_frames=2, silence_frames=30))

    # Get speech detected
    vad.process(np.full((160, 1), 0.1))
    vad.process(np.full((160, 1), 0.1))

    # 29 silent frames
    for _ in range(29):
        assert vad.process(np.full((160, 1), 0.005))[0] is False
        assert vad.silence_detected is False

    # 30th silent frame
    assert vad.process(np.full((160, 1), 0.005))[0] is False
    assert vad.silence_detected is True


def test_analyze_calibration_normal_noise():
    """Normal noise yields threshold = P90 + base_threshold."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.008))

    # Deterministic steady background noise around 0.02
    energies = [
        0.0198, 0.0200, 0.0201, 0.0199, 0.0202,
        0.0200, 0.0199, 0.0201, 0.0198, 0.0200,
        0.0202, 0.0199, 0.0201, 0.0200, 0.0199,
        0.0201, 0.0200, 0.0198, 0.0202, 0.0200,
        0.0199, 0.0201, 0.0200, 0.0198, 0.0200,
        0.0201, 0.0199, 0.0202, 0.0200, 0.0199,
        0.0201, 0.0200, 0.0198, 0.0200, 0.0201,
        0.0199, 0.0202, 0.0200, 0.0199, 0.0201,
        0.0200, 0.0198, 0.0200, 0.0201, 0.0199,
    ]
    samples = [np.full((160, 1), e) for e in energies]

    threshold, noise_floor, is_degenerate = vad.analyze_calibration(samples, percentile=90.0)

    assert is_degenerate is False
    assert noise_floor > 0.0
    # P90 ~ 0.0201 + base 0.008 = ~0.0281
    assert 0.025 < threshold < 0.032


def test_analyze_calibration_degenerate_near_zero():
    """Near-zero energy (e.g., ASUS AI mic) is detected as degenerate relative to base threshold."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.008))

    # Simulate near-zero energy frames (degenerate microphone)
    samples = [np.full((160, 1), 0.0001) for _ in range(50)]

    threshold, noise_floor, is_degenerate = vad.analyze_calibration(samples, percentile=90.0)

    assert is_degenerate is True
    assert threshold == 0.0
    # Floating point precision
    assert abs(noise_floor - 0.0001) < 1e-10


def test_analyze_calibration_with_outlier_spikes():
    """P90 is robust to transient spikes; uses default NumPy percentile behavior.

    30 frames at 0.02, 3 frames at 0.5 (spikes) - total 33 frames.
    P90 of 33 frames = 30th index (0-indexed). With 30 low + 3 high, P90 should be ~0.02
    """
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.008))

    # 30 frames at 0.02, 3 frames at 0.5 (spikes) - total 33 frames (~1s at 30ms frames)
    base_samples = [np.full((160, 1), 0.02) for _ in range(30)]
    spike_samples = [np.full((160, 1), 0.5) for _ in range(3)]
    samples = base_samples + spike_samples

    threshold, noise_floor, is_degenerate = vad.analyze_calibration(samples, percentile=90.0)

    assert is_degenerate is False
    # P90 ignores top 10% (the spikes), so ~0.02 + 0.008 = ~0.028
    # Std-based would be ~0.12 std, threshold ~0.4 (too high)
    assert 0.025 < threshold < 0.032
    assert noise_floor == 0.02


def test_analyze_calibration_empty_samples():
    """Empty samples returns current threshold and degenerate flag."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.015))

    threshold, noise_floor, is_degenerate = vad.analyze_calibration([])

    assert is_degenerate is True
    assert threshold == 0.015  # Returns current threshold
    assert noise_floor == 0.0


def test_apply_calibration_updates_state():
    """apply_calibration stores threshold, noise_floor, and sets calibrated."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.01))

    vad.apply_calibration(0.025, 0.006)

    assert vad.config.energy_threshold == 0.025
    assert vad.noise_floor == 0.006
    assert vad.calibrated is True


def test_calibrated_state_preserved_after_reset():
    """Calibration state survives reset(); only counters are cleared."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.01))

    samples = [np.full((160, 1), 0.005) for _ in range(10)]
    vad.analyze_calibration(samples)
    vad.apply_calibration(0.015, 0.005)

    assert vad.calibrated is True
    original_threshold = vad.config.energy_threshold

    # Drive VAD through normal processing
    vad.process(np.full((160, 1), 0.1))  # Speech
    vad.process(np.full((160, 1), 0.0))   # Silence

    vad.reset()

    assert vad.calibrated is True
    assert vad.config.energy_threshold == original_threshold
    assert vad._speech_counter == 0
    assert vad._silence_counter == 0


def test_calibration_percentile_configurable():
    """Changing percentile changes threshold (P50 vs P90)."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.008))

    # Distribution: mostly 0.02, some 0.05 (both above base 0.008)
    samples = [np.full((160, 1), 0.02) for _ in range(80)]
    samples += [np.full((160, 1), 0.05) for _ in range(20)]

    threshold_50, _, _ = vad.analyze_calibration(samples, percentile=50.0)
    threshold_90, _, _ = vad.analyze_calibration(samples, percentile=90.0)

    # P50 ~ 0.02 -> 0.028
    # P90 ~ 0.05 -> 0.058
    assert threshold_50 < threshold_90
    assert 0.026 < threshold_50 < 0.032
    assert 0.055 < threshold_90 < 0.065


def test_base_threshold_preserved_for_degenerate_check():
    """_base_energy_threshold remains at config initial value."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.008))

    # After analyzing a normal window, base should be unchanged
    samples = [np.full((160, 1), 0.005) for _ in range(20)]
    vad.analyze_calibration(samples)

    assert vad.base_energy_threshold == 0.008
    assert vad.config.energy_threshold == 0.008  # Not yet applied


def test_degenerate_at_exact_base_threshold():
    """P90 == base_threshold is NOT degenerate (strictly less)."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.01))

    samples = [np.full((160, 1), 0.01) for _ in range(20)]

    _, _, is_degenerate = vad.analyze_calibration(samples, percentile=90.0)

    assert is_degenerate is False


def test_calibrate_legacy_api_rejects_degenerate():
    """Legacy calibrate() does not accept degenerate window."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.008))

    # Degenerate samples
    samples = [np.full((160, 1), 0.0001) for _ in range(10)]
    vad.calibrate(samples)

    # Should remain uncalibrated
    assert vad.calibrated is False


def test_calibrate_legacy_api_accepts_valid():
    """Legacy calibrate() accepts valid window."""
    vad = VoiceActivityDetector(VADConfig(energy_threshold=0.008))

    # Valid samples
    samples = [np.full((160, 1), 0.02) for _ in range(10)]
    vad.calibrate(samples)

    # Should be calibrated
    assert vad.calibrated is True
    # threshold = P90 (0.02) + base (0.008) = 0.028
    assert 0.025 < vad.config.energy_threshold < 0.032