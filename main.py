"""
Main entry point for JARVIS.
"""

from core.executor import CommandExecutor
from core.runtime import JarvisRuntime
from core.state import StateManager
from voice.service import VoiceService


def main() -> None:
    """
    Application entry point.
    """
    voice = VoiceService()
    executor = CommandExecutor()
    state_manager = StateManager()
    runtime = JarvisRuntime(
        voice=voice,
        executor=executor,
        state_manager=state_manager,
    )
    runtime.run()


if __name__ == "__main__":
    main()
