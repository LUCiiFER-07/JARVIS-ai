"""
JARVIS Runtime Foundation (Phase 4).

Owns startup, lifecycle, state management, and one command iteration loop.
"""

from core.commands import CommandType
from core.executor import CommandExecutor
from core.parser import CommandParser
from core.state import JarvisState, StateManager
from speech.exceptions import SpeechError
from utils.logger import get_logger
from voice.exceptions import VoiceError
from voice.service import VoiceService

logger = get_logger(__name__)


class JarvisRuntime:
    """
    Runtime abstraction for JARVIS.

    Provides lifecycle control, state management, and a testable command iteration loop.
    """

    def __init__(
        self,
        voice: VoiceService,
        executor: CommandExecutor,
        state_manager: StateManager,
    ) -> None:
        self._voice = voice
        self._executor = executor
        self._state_manager = state_manager

    @property
    def state_manager(self) -> StateManager:
        """Return the state manager instance."""
        return self._state_manager

    @property
    def current_state(self) -> JarvisState:
        """Return the current application state."""
        return self._state_manager.current_state

    def process_command(self) -> bool:
        """
        Run a single command iteration.

        Returns False when JARVIS should stop, otherwise True.
        """
        self._state_manager.transition(JarvisState.LISTENING)
        result = self._voice.record_and_transcribe()

        logger.info(
            "Speech successfully transcribed."
        )

        self._state_manager.transition(JarvisState.TRANSCRIBING)

        print("\n📝 Transcription")
        print("-" * 40)
        print(result.text)

        print("\nDetected Language:", result.language)

        command = CommandParser.parse(result.text)

        logger.info(
            "Command detected: %s",
            command.command_type.value,
        )

        self._state_manager.transition(JarvisState.EXECUTING)
        response = self._executor.execute(command)

        print("\n🤖 JARVIS")
        print("-" * 40)
        print(response)

        self._state_manager.transition(JarvisState.IDLE)

        return command.command_type is not CommandType.EXIT

    def run(self) -> None:
        """
        Start JARVIS and run the continuous listening loop.
        """
        logger.info("JARVIS started.")

        try:
            self._state_manager.transition(JarvisState.INITIALIZING)
            self._voice.select_microphone()
            self._state_manager.transition(JarvisState.IDLE)

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
                    self._state_manager.transition(JarvisState.ERROR)
                    print(f"\n🎤 Voice Error: {error}")
                    print("Returning to listening...")
                    self._state_manager.transition(JarvisState.IDLE)

                except SpeechError as error:
                    logger.error("Speech error: %s", error)
                    self._state_manager.transition(JarvisState.ERROR)
                    print(f"\n🗣 Speech Error: {error}")
                    print("Returning to listening...")
                    self._state_manager.transition(JarvisState.IDLE)

        except KeyboardInterrupt:
            logger.info("Application interrupted by user.")
            self._state_manager.transition(JarvisState.ERROR)
            print("\n\nGoodbye, Sir!")

        except Exception:
            logger.exception("Unexpected application error.")
            self._state_manager.transition(JarvisState.ERROR)
            print("\nUnexpected error occurred.")

        finally:
            self._state_manager.transition(JarvisState.OFFLINE)
            logger.info("JARVIS stopped.")
