"""
JARVIS Runtime Foundation (Phase 3).

Owns startup, lifecycle, and one command iteration loop while preserving current behavior.
"""

from core.commands import CommandType
from core.executor import CommandExecutor
from core.parser import CommandParser
from speech.exceptions import SpeechError
from utils.logger import get_logger
from voice.exceptions import VoiceError
from voice.service import VoiceService

logger = get_logger(__name__)


class JarvisRuntime:
    """
    Runtime abstraction for JARVIS.

    Provides lifecycle control and a testable command iteration loop.
    """

    def __init__(
        self,
        voice: VoiceService,
        executor: CommandExecutor,
    ) -> None:
        self._voice = voice
        self._executor = executor

    def process_command(self) -> bool:
        """
        Run a single command iteration.

        Returns False when JARVIS should stop, otherwise True.
        """

        result = self._voice.record_and_transcribe()

        logger.info(
            "Speech successfully transcribed."
        )

        print("\n📝 Transcription")
        print("-" * 40)
        print(result.text)

        print("\nDetected Language:", result.language)

        command = CommandParser.parse(result.text)

        logger.info(
            "Command detected: %s",
            command.command_type.value,
        )

        response = self._executor.execute(command)

        print("\n🤖 JARVIS")
        print("-" * 40)
        print(response)

        return command.command_type is not CommandType.EXIT

    def run(self) -> None:
        """
        Start JARVIS and run the continuous listening loop.
        """

        logger.info("JARVIS started.")

        try:
            self._voice.select_microphone()

            print("\n" + "=" * 50)
            print("🤖 JARVIS is ready.")
            print("🎤 Listening for commands...")
            print("Press Ctrl+C to stop.")
            print("=" * 50)

            while True:
                try:
                    should_continue = self.process_command()

                    if not should_continue:
                        break

                    print("\n🎤 Listening again...")

                except VoiceError as error:
                    logger.error("Voice error: %s", error)
                    print(f"\n🎤 Voice Error: {error}")
                    print("Returning to listening...")

                except SpeechError as error:
                    logger.error("Speech error: %s", error)
                    print(f"\n🗣 Speech Error: {error}")
                    print("Returning to listening...")

        except KeyboardInterrupt:
            logger.info("Application interrupted by user.")
            print("\n\nGoodbye, Sir!")

        except Exception:
            logger.exception("Unexpected application error.")
            print("\nUnexpected error occurred.")

        finally:
            logger.info("JARVIS stopped.")
