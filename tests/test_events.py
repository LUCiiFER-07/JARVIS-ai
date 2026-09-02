"""
Tests for the JARVIS Central Event System (Phase 5).
"""

from pathlib import Path
from unittest.mock import MagicMock

from core.events import EventBus, EventType, JarvisEvent
from core.executor import CommandExecutor
from core.runtime import JarvisRuntime
from core.state import JarvisState, StateManager
from speech.models import SpeechResult
from voice.service import VoiceService


def test_event_bus_subscription_and_publish() -> None:
    """Test subscribing to events and publishing them to callbacks."""
    bus = EventBus()
    events_received: list[JarvisEvent] = []

    def callback(event: JarvisEvent) -> None:
        events_received.append(event)

    bus.subscribe(EventType.COMMAND_DETECTED, callback)

    event = bus.publish_type(EventType.COMMAND_DETECTED, {"text": "hello"})

    assert len(events_received) == 1
    assert events_received[0] == event
    assert events_received[0].event_type == EventType.COMMAND_DETECTED
    assert events_received[0].data["text"] == "hello"


def test_event_bus_unsubscribe() -> None:
    """Test unsubscribing from event types."""
    bus = EventBus()
    events_received: list[JarvisEvent] = []

    def callback(event: JarvisEvent) -> None:
        events_received.append(event)

    bus.subscribe(EventType.JARVIS_STARTED, callback)
    bus.unsubscribe(EventType.JARVIS_STARTED, callback)

    bus.publish_type(EventType.JARVIS_STARTED)

    assert len(events_received) == 0


def test_event_bus_clear() -> None:
    """Test clearing all subscribers."""
    bus = EventBus()
    events_received: list[JarvisEvent] = []

    def callback(event: JarvisEvent) -> None:
        events_received.append(event)

    bus.subscribe(EventType.JARVIS_STARTED, callback)
    bus.clear()

    bus.publish_type(EventType.JARVIS_STARTED)
    assert len(events_received) == 0


def test_state_manager_publishes_state_changed_events() -> None:
    """Test StateManager publishes STATE_CHANGED events to EventBus when provided."""
    bus = EventBus()
    events: list[JarvisEvent] = []

    bus.subscribe(EventType.STATE_CHANGED, lambda e: events.append(e))

    sm = StateManager(initial_state=JarvisState.OFFLINE, event_bus=bus)
    sm.transition(JarvisState.INITIALIZING)
    sm.transition(JarvisState.IDLE)

    assert len(events) == 2
    assert events[0].data["old_state"] == JarvisState.OFFLINE
    assert events[0].data["new_state"] == JarvisState.INITIALIZING
    assert events[1].data["old_state"] == JarvisState.INITIALIZING
    assert events[1].data["new_state"] == JarvisState.IDLE


def test_runtime_event_bus_integration() -> None:
    """Test JarvisRuntime publishes lifecycle events to EventBus."""
    bus = EventBus()
    event_types_received: list[EventType] = []

    bus.subscribe(EventType.STATE_CHANGED, lambda e: event_types_received.append(e.event_type))

    mock_voice = MagicMock(spec=VoiceService)
    mock_voice.record_and_transcribe.return_value = SpeechResult(
        text="exit",
        language="en",
        audio_path=Path("audio.wav"),
    )

    mock_executor = MagicMock(spec=CommandExecutor)
    mock_executor.execute.return_value = "Goodbye, Sir."

    state_manager = StateManager(event_bus=bus)
    runtime = JarvisRuntime(
        voice=mock_voice,
        executor=mock_executor,
        state_manager=state_manager,
        event_bus=bus,
    )

    runtime.run()

    assert EventType.STATE_CHANGED in event_types_received
    assert runtime.event_bus is bus
