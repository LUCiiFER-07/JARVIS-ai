"""
Voice recording module for JARVIS.

This module records audio from the default microphone and saves it as a WAV file.
"""

import time
from collections import deque
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

import voice.config
from utils.logger import get_logger
from voice.exceptions import RecordingError
from voice.vad import VADConfig, VoiceActivityDetector

logger = get_logger(__name__)


class VoiceRecorder:
    """Handles recording audio."""

    def __init__(
            self,
            config: voice.config.VoiceConfig | None = None,
    ) -> None:
        self.config = config or voice.config.VoiceConfig()

        self.vad = VoiceActivityDetector(
            VADConfig(
                energy_threshold=self.config.vad_energy_threshold,
                speech_frames=self.config.vad_speech_frames,
                silence_frames=self.config.vad_silence_frames,
            )
        )

        self._pre_roll = deque(
            maxlen=self.config.pre_roll_frames
        )

    def _frame_size(self) -> int:
        """Return the number of samples in one VAD frame.
        """

        return int(
            self.config.sample_rate
            * self.config.vad_frame_duration_ms
            / 1000
        )

    def _speech_detected(
            self,
            frame: np.ndarray,
    ) -> bool:
        """
        Check whether a frame contains speech.
        """

        speech, energy = self.vad.process(frame)

        logger.debug(
            "Energy: %.5f | Speech: %s",
            energy,
            speech,
        )

        return speech

    def _create_stream(self) -> sd.InputStream:
        """
        Create an audio input stream using the number of channels
        supported by the selected microphone.
        """

        device_info = sd.query_devices(
            self.config.device,
        )

        max_input_channels = int(
            device_info["max_input_channels"]
        )

        if max_input_channels <= 0:
            raise RecordingError(
                "Selected device has no input channels."
            )

        # Use stereo when available, otherwise fall back to mono.
        channels = min(max_input_channels, 2)

        logger.info(
            "Opening microphone stream | Device=%s | Channels=%d | Sample Rate=%d Hz",
            self.config.device,
            channels,
            self.config.sample_rate,
        )

        return sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=channels,
            dtype="float32",
            device=self.config.device,
            blocksize=self._frame_size(),
        )

    def _read_frame(
        self,
        stream: sd.InputStream,
    ) -> np.ndarray:
        """
        Read one frame from the microphone and convert stereo
        input to mono audio.
        """

        frame, overflowed = stream.read(
            self._frame_size()
        )

        if overflowed:
            logger.warning(
                "Audio input overflow detected."
            )

        # Convert stereo → mono.
        if frame.ndim == 2 and frame.shape[1] > 1:
            frame = np.mean(
                frame,
                axis=1,
                keepdims=True,
            )

        return frame

    def _store_pre_roll(
            self,
            frame: np.ndarray,
    ) -> None:
        """
        Store one frame in the rolling pre-roll buffer.
        """

        self._pre_roll.append(frame.copy())

    def _consume_pre_roll(
            self,
    ) -> list[np.ndarray]:
        """
        Return all buffered frames and clear the buffer.
        """
        frames = list(self._pre_roll)

        self._pre_roll.clear()

        return frames

    def _clear_pre_roll(self) -> None:
        """
        Remove all bufferef audio.
        """

        self._pre_roll.clear()

    def _save_audio(
            self,
            audio: np.ndarray,
            output_path: Path,
    )-> None:
        """
        Save audio to disk.
        """

        sf.write(
            output_path,
            audio,
            self.config.sample_rate,
        )

        logger.info(
            "Recording saved successfully: %s",
            output_path,
        )

    def _collect_audio(self) -> np.ndarray:
        """
        Collect audio using streaming VAD.

        The recorder waits for speech for a limited amount of time.
        Once speech begins, recording continues until enough silence
        is detected or the maximum recording duration is reached.
        """

        recorded_frames: list[np.ndarray] = []
        recording = False

        # Reset VAD before every recording.
        self.vad.reset()
        self._clear_pre_roll()

        # Track when listening begins.
        listening_started = time.monotonic()

        # Will be assigned when speech starts.
        recording_started: float | None = None

        with self._create_stream() as stream:

            self._calibrate(stream)

            logger.info("Listening...")

            while True:

                frame = self._read_frame(stream)

                self._store_pre_roll(frame)

                speech, _ = self.vad.process(frame)
                # -------------------------
                # Waiting for speech
                # -------------------------

                if not recording:

                    elapsed = time.monotonic() - listening_started

                    if speech:

                        logger.info("Speech detected.")

                        recording = True
                        recording_started = time.monotonic()

                        recorded_frames.extend(
                        self._consume_pre_roll()
                        )

                    elif elapsed >= self.config.speech_start_timeout:

                        logger.info(
                            "No speech detected within %.1f seconds.",
                            self.config.speech_start_timeout,
                        )

                        raise RecordingError(
                            "No speech detected within the timeout period."
                        )

                    continue

                # -------------------------
                # Recording speech
                # -------------------------

                recorded_frames.append(frame)

                # -------------------------
                # Maximum recording duration
                # -------------------------

                if recording_started is not None:

                    recording_elapsed = (
                        time.monotonic() - recording_started
                    )

                    if (
                        recording_elapsed
                        >= self.config.max_recording_duration
                    ):

                        logger.info(
                            "Maximum recording duration reached."
                        )

                        break

                # -------------------------
                # Stop after enough silence
                # -------------------------

                if self.vad.silence_detected:

                    logger.info("Speech finished.")

                    break

        if not recorded_frames:
            raise RecordingError(
            "No speech was detected."
            )

        return np.concatenate(
            recorded_frames,
            axis=0,
        )
    
    def record(
        self,
        filename: str = "test.wav",
    ) -> Path:
        """
        Record audio using the configured microphone.

        Args:
            filename:
                Name of the output WAV file.

        Returns:
            Path to the recorded WAV file.
        """

        recordings_dir =  Path("recordings")
        recordings_dir.mkdir(exist_ok=True)

        output_path = recordings_dir / filename

        try:

            logger.info(
                "Recording started."
            )
            audio =  self._collect_audio()

            sf.write(output_path, audio, self.config.sample_rate)

            logger.info("Recording saved successfully: %s", output_path)

            return output_path

        except RecordingError:
            raise

        except Exception as error:
            logger.exception("Recording failed.")
            raise RecordingError(
                "Failed to record audio."
        ) from error

    def _calibrate(
        self,
        stream: sd.InputStream,
    ) -> None:
        """
        Calibrate the VAD using background noise
        captured from the selected microphone.
        """

        calibration_frames: list[np.ndarray] = []

        calibration_started = time.monotonic()

        logger.info(
            "Calibrating microphone. Please remain silent..."
        )

        while (
            time.monotonic() - calibration_started
            < self.config.vad_calibration_duration
        ):
            frame = self._read_frame(stream)

            calibration_frames.append(frame)

        self.vad.calibrate(
            calibration_frames,
            threshold_multiplier=self.config.vad_threshold_multiplier,
        )

        logger.info(
            "VAD calibrated | Noise floor: %.5f | "
            "Threshold: %.5f",
            self.vad.noise_floor,
            self.vad.config.energy_threshold,
        )