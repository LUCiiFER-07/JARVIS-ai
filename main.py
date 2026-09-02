"""
Main entry point for JARVIS.
"""

from core.events import EventBus
from core.executor import CommandExecutor
from core.runtime import JarvisRuntime
from core.state import StateManager
from voice.service import VoiceService


def main() -> None:
    """
    Application entry point.
    """
    event_bus = EventBus()
    voice = VoiceService()
    executor = CommandExecutor()
    state_manager = StateManager(event_bus=event_bus)
    runtime = JarvisRuntime(
        voice=voice,
        executor=executor,
        state_manager=state_manager,
        event_bus=event_bus,
    )
    runtime.run()


if __name__ == "__main__":
    main()
