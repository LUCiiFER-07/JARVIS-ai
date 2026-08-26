"""
Audio device discovery utilities.
"""

import sounddevice as sd

from utils.logger import get_logger
from voice.device import AudioDevice

logger = get_logger(__name__)


class AudioDevices:
    """
    Utility class for listing audio input devices.
    """

    @staticmethod
    def list_input_devices() -> list[AudioDevice]:

        """
        Return a clean list of microphones. 
        """

        devices = sd.query_devices()
        hostapis = sd.query_hostapis()

        microphones: list[AudioDevice] = []

        seen: set[str] = set()

        # We only want modern Windows devices.
        preferred_api = "Windows WASAPI"

        excluded_keywords = (
            "Stereo Mix",
            "PC Speaker",
            "System Virtual",
            "Line Out",
            "Primary Sound",
            "Microsoft Sound Mapper",
            "Output",
        )

        for index, device in enumerate(devices):

            if device["max_input_channels"] <= 0:
                continue

            api_name = hostapis[device["hostapi"]]["name"]

            if api_name != preferred_api:
                continue

            name = device["name"].strip()

            if any(word in name for word in excluded_keywords):
                continue

            if name in seen:
                continue

            seen.add(name)

            microphones.append(
                AudioDevice(
                    index=index,
                    name=name,
                    channels=device["max_input_channels"],
                    sample_rate=int(device["default_samplerate"]),
                )
            ) 

        microphones.sort(
            key=lambda d: d.name.lower()
        )  

        logger.info(
            "Discovered %d microphone(s).",
            len(microphones),
        ) 
              
        return microphones
