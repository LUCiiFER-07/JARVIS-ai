from speech.exceptions import SpeechError
from utils.logger import get_logger
from voice.exceptions import VoiceError
from voice.service import VoiceService

logger = get_logger(__name__)


def main() -> None:
    """
    Entry point for JARVIS.
    """

    logger.info(
        "JARVIS started."
    )

    try:
        voice = VoiceService()

        voice.select_microphone()

        result = voice.record_and_transcribe()

        logger.info(
            "Speech successfully transcribed."
        )

        print("\n📝 Transcription")
        print("-" * 40)
        print(result.text)

        print("\nDetected Language:", result.language)

    except VoiceError as error:

        logger.error(
            "Voice error: %s",
            error,
        )

        print(f"\n🎤 Voice Error: {error}")

    except SpeechError as error:

        logger.error(
            "Speech error: %s",
            error,
        )

        print(f"\n🗣 Speech Error: {error}")

    except KeyboardInterrupt:

        logger.info(
            "Application interrupted by user."
        )

        print("\n\nGoodbye!")

    except Exception:

        logger.exception(
            "Unexpected application error."
        )

        print("\nUnexpected error occurred.")

    finally:

        logger.info(
            "JARVIS stopped."
        )


if __name__ == "__main__":
    main()