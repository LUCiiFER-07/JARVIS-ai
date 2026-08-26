from core.commands import CommandType
from core.executor import CommandExecutor
from core.parser import CommandParser
from speech.exceptions import SpeechError
from utils.logger import get_logger
from voice.exceptions import VoiceError
from voice.service import VoiceService

logger = get_logger(__name__)


def process_command(
    voice: VoiceService,
    executor: CommandExecutor,
) -> bool:
    """
    Record, transcribe, parse, and execute one command.

    Returns:
        False when JARVIS should stop.
        True when JARVIS should continue listening.
    """

    result = voice.record_and_transcribe()

    logger.info(
        "Speech successfully transcribed."
    )

    print("\n📝 Transcription")
    print("-" * 40)
    print(result.text)

    print("\nDetected Language:", result.language)

    command = CommandParser.parse(
        result.text
    )

    logger.info(
        "Command detected: %s",
        command.command_type.value,
    )

    response = executor.execute(
        command
    )

    print("\n🤖 JARVIS")
    print("-" * 40)
    print(response)

    return command.command_type is not CommandType.EXIT

def main() -> None:
    """
    Entry point for JARVIS.
    """

    logger.info(
        "JARVIS started."
    )

    voice: VoiceService | None = None

    try:
        voice = VoiceService()

        voice.select_microphone()

        executor = CommandExecutor()

        print("\n" + "=" * 50)
        print("🤖 JARVIS is ready.")
        print("🎤 Listening for commands...")
        print("Press Ctrl+C to stop.")
        print("=" * 50)

        while True:

            try:
                should_continue = process_command(
                    voice,
                    executor,
                )

                if not should_continue:
                    break

                print("\n🎤 Listening again...")

            except VoiceError as error:

                logger.error(
                    "Voice error: %s",
                    error,
                )

                print(
                    f"\n🎤 Voice Error: {error}"
                )

                print(
                    "Returning to listening..."
                )

            except SpeechError as error:

                logger.error(
                    "Speech error: %s",
                    error,
                )

                print(
                    f"\n🗣 Speech Error: {error}"
                )

                print(
                    "Returning to listening..."
                )

    except KeyboardInterrupt:

        logger.info(
            "Application interrupted by user."
        )

        print("\n\nGoodbye, Sir!")

    except Exception:

        logger.exception(
            "Unexpected application error."
        )

        print(
            "\nUnexpected error occurred."
        )

    finally:

        logger.info(
            "JARVIS stopped."
        )


if __name__ == "__main__":
    main()

