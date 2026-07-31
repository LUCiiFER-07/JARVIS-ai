"""
Settings manager for the voice module.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, ClassVar

from utils.logger import get_logger

logger = get_logger(__name__)


class VoiceSettings:
    """Manage voice-related settings."""

    SETTINGS_FILE: ClassVar[Path] = Path("voice") / "settings.json"

    DEFAULT_SETTINGS: ClassVar[dict[str, Any]] = {
        "audio": {
            "input_device": None,
            "output_device": None,
        }
    }

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load settings from disk."""

        if not cls.SETTINGS_FILE.exists():
            cls.save(cls.DEFAULT_SETTINGS)
            return deepcopy(cls.DEFAULT_SETTINGS)

        try:
            with open(
                cls.SETTINGS_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                
                settings = json.load(file)

            logger.info(
                "Voice settings loaded."
            )

            return settings

        except json.JSONDecodeError:
            
            logger.warning(
                "Voice settings file is corrupted. Restoring defaults."
            )

            cls.save(cls.DEFAULT_SETTINGS)

            return deepcopy(cls.DEFAULT_SETTINGS)

    @classmethod
    def save(cls, settings: dict[str, Any]) -> None:
        """Save settings to disk."""

        cls.SETTINGS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(cls.SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)
            logger.info("Voice settings saved.")


    @classmethod
    def get_input_device(cls) -> int | None:
        """Return the saved input device index."""  

        settings = cls.load()
        return settings.get(
            "audio",
            {},
        ).get(
            "input_device",
        )


    @classmethod
    def set_input_device(
        cls, 
        device_index: int | None,
    ) -> None:
        """Save the selected input device."""

        settings = cls.load()
        settings["audio"]["input_device"] = device_index
        cls.save(settings)      


    @classmethod
    def clear_input_device(cls) -> None:
        """
        Remove the saved input microphone.
        """


        settings = cls.load()
        settings["audio"]["input_device"] = None
        cls.save(settings)
        logger.info("Saved input device cleared.")