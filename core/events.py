"""
Central Event Bus for JARVIS (Phase 5).

Defines event types, event data structures, and a lightweight publish-subscribe EventBus.
"""

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    """
    Authoritative event types for JARVIS.
    """

    STATE_CHANGED = "state_changed"
    VOICE_STARTED = "voice_started"
    VOICE_RECORDED = "voice_recorded"
    SPEECH_TRANSCRIBED = "speech_transcribed"
    COMMAND_DETECTED = "command_detected"
    COMMAND_EXECUTED = "command_executed"
    ERROR_OCCURRED = "error_occurred"
    JARVIS_STARTED = "jarvis_started"
    JARVIS_STOPPED = "jarvis_stopped"


@dataclass(frozen=True)
class JarvisEvent:
    """
    Represents an immutable event published on the JARVIS EventBus with immutable payload.
    """

    event_type: EventType
    timestamp: float = field(default_factory=time.time)
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.data, MappingProxyType):
            copied = dict(self.data) if self.data else {}
            object.__setattr__(self, "data", MappingProxyType(copied))


class EventBus:
    """
    Publish-subscribe event bus for decoupled component communication with subscriber isolation
    and reentrant publication safety.
    """

    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[Callable[[JarvisEvent], None]]] = {}

    def subscribe(
        self, event_type: EventType, callback: Callable[[JarvisEvent], None]
    ) -> None:
        """
        Subscribe a callback function to a specific event type.
        Duplicate subscriptions are ignored.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(
        self, event_type: EventType, callback: Callable[[JarvisEvent], None]
    ) -> None:
        """
        Unsubscribe a callback function from a specific event type.
        Nonexistent subscriptions are safely ignored.
        """
        if (
            event_type in self._subscribers
            and callback in self._subscribers[event_type]
        ):
            self._subscribers[event_type].remove(callback)

    def publish(self, event: JarvisEvent) -> None:
        """
        Publish an event to all subscribers registered for its event type.
        Uses a subscriber snapshot for reentrancy safety and isolates subscriber exceptions.
        """
        subscribers = list(self._subscribers.get(event.event_type, []))
        for callback in subscribers:
            try:
                callback(event)
            except Exception:
                logger.exception(
                    "Error in event subscriber callback for %s", event.event_type.value
                )

    def publish_type(
        self, event_type: EventType, data: dict[str, Any] | None = None
    ) -> JarvisEvent:
        """
        Convenience method to create and publish an event by type and data.
        """
        event = JarvisEvent(event_type=event_type, data=data or {})
        self.publish(event)
        return event

    def clear(self) -> None:
        """
        Remove all subscribers across all event types (primarily for testing).
        """
        self._subscribers.clear()
