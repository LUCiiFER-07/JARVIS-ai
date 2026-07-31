"""Manages microphone selection."""

from utils.logger import get_logger

from voice.device import AudioDevice
from voice.discovery import AudioDevices
from voice.exceptions import DeviceNotFoundError
from voice.settings import VoiceSettings

logger = get_logger(__name__)


class DeviceManager:
    """Handles microphone discovery and selection."""

    @staticmethod
    def _print_microphone(
        device: AudioDevice,
        title: str,
    ) -> None:
        """
        Display microphone information.
        """

        print(f"\n🎤 {title}")
        print("─" * 40)

        print(f"Name       : {device.name}")
        print(f"Index      : {device.index}")
        print(f"Channels   : {device.channels}")
        print(f"Sample Rate: {device.sample_rate}Hz")

    @staticmethod
    def _print_microphone_list(
        devices: list[AudioDevice],
    ) -> None:
        """
        Display all available microphones.
        """

        print("\n🎤 Available Microphones")
        print("─" * 40)

        for number, device in enumerate(devices, start=1):
            print(
                f"{number}." 
                f"{device.name}"
                f"({device.sample_rate}Hz)"
            )

    @staticmethod
    def _show_menu() -> None:
            """
            Display microphone options.
            """
    
            print("\n⚙️  Microphone Options")
            print("─" * 40)
    
            print("1. Continue with the saved microphone")
            print("2. Change microphone")
            print("3. Forget saved microphone")        

    @staticmethod
    def _choose_microphone() -> AudioDevice:
        """
        Ask the user to choose a microphone.
        
        Returns:
            The selected AudioDevice.
        """

        devices = AudioDevices.list_input_devices()

        if not devices:
            raise DeviceNotFoundError("No microphone found.")

        DeviceManager._print_microphone_list(devices)

        while True:
            try:
                choice = int(input("\nChoose microphone: "))

                if 1 <= choice <= len(devices):
                    selected = devices[choice - 1]

                    #Save the user's choice.
                    VoiceSettings.set_input_device(selected.index)

                    logger.info(
                        "Microphone selected: %s (Index=%d)",
                        selected.name,
                        selected.index,
                    )

                    print("\n✅ Microphone saved successfully.")

                    return selected

                print(f"Please choose a number between 1 and {len(devices)}.")

            except ValueError:
                print("Please enter a valid number.") 

    @staticmethod
    def _ask_saved_microphone(device:AudioDevice) -> int:
        """
        Ask the user what to do with the saved microphone.
        
        Args:
            device: The currently saved microphone.
            
        Returns:
            1 -> Continue using the saved microphone.
            2 -> change microphone.
            3 -> Forget saved microphone.
        """

        DeviceManager._print_microphone(
           device,
           "Saved Microphone",
       )

        DeviceManager._show_menu()

        while True:
            try:
                choice = int(input("\nChoose an option(1-3): "))

                if choice in (1, 2, 3):
                    return choice

                print("Please choose 1, 2 or 3.")

            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def get_microphone() -> AudioDevice:
        """
        Return the saved microphone if available.
        Otherwise ask the user to choose one.
        """

        devices = AudioDevices.list_input_devices()

        if not devices:
            raise DeviceNotFoundError("No microphone found.")

        saved_index = VoiceSettings.get_input_device()

        #Check if the saved microphone still exists.

        if saved_index is not None:
            saved_device = next(
                    (
                        device 
                        for device in devices
                        if device.index == saved_index
                    ),
                    None,
            )

            if saved_device is not None:
                choice = DeviceManager._ask_saved_microphone(saved_device)

                if choice == 1:

                    logger.info(
                        "Using saved microphone: %s",
                        saved_device.name,
                    )

                    return saved_device

                if choice == 2:

                    logger.info(
                        "User requested microphone change."
                    )

                    return DeviceManager._choose_microphone()

                if choice == 3:
                    VoiceSettings.clear_input_device()

                    logger.info(
                        "Saved microphone removed."
                    )

                    print("\n🗑 Saved microphone removed.")

                    return DeviceManager._choose_microphone()

        #Saved microphone doesn't exist anymore
        # or no microphone has been saved yet.
        return DeviceManager._choose_microphone()                   

