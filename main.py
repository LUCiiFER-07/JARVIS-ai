"""
Main entry point for JARVIS.
"""

from core.executor import CommandExecutor
from core.runtime import JarvisRuntime
from voice.service import VoiceService


def main() -> None:
    """
    Application entry point.
    """
    voice = VoiceService()
    executor = CommandExecutor()
    runtime = JarvisRuntime(voice=voice, executor=executor)
    runtime.run()


if __name__ == "__main__":
    main()
