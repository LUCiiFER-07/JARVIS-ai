"""
Central State Manager for JARVIS (Phase 5).

Defines authoritative application states and state transition logic, with EventBus integration.
"""

from enum import Enum
from typing import ClassVar

from core.events import EventBus, EventType


class JarvisState(Enum):
    """
    Authoritative application states for JARVIS.
    """

    OFFLINE = "offline"
    INITIALIZING = "initializing"
    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    SEARCHING = "searching"
    USING_TOOL = "using_tool"
    EXECUTING = "executing"
    WAITING_FOR_PERMISSION = "waiting_for_permission"
    SPEAKING = "speaking"
    PAUSED = "paused"
    ERROR = "error"


class InvalidStateTransitionError(Exception):
    """
    Raised when an invalid state transition is attempted.
    """


class StateManager:
    """
    Manages JARVIS application state and validates state transitions.
    """

    ALLOWED_TRANSITIONS: ClassVar[dict[JarvisState, set[JarvisState]]] = {
        JarvisState.OFFLINE: {JarvisState.INITIALIZING, JarvisState.IDLE, JarvisState.LISTENING, JarvisState.ERROR},
        JarvisState.INITIALIZING: {JarvisState.IDLE, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.IDLE: {JarvisState.LISTENING, JarvisState.PAUSED, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.LISTENING: {JarvisState.TRANSCRIBING, JarvisState.IDLE, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.TRANSCRIBING: {JarvisState.EXECUTING, JarvisState.THINKING, JarvisState.IDLE, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.THINKING: {JarvisState.SEARCHING, JarvisState.USING_TOOL, JarvisState.WAITING_FOR_PERMISSION, JarvisState.EXECUTING, JarvisState.SPEAKING, JarvisState.IDLE, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.SEARCHING: {JarvisState.THINKING, JarvisState.EXECUTING, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.USING_TOOL: {JarvisState.EXECUTING, JarvisState.SPEAKING, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.WAITING_FOR_PERMISSION: {JarvisState.EXECUTING, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.EXECUTING: {JarvisState.SPEAKING, JarvisState.IDLE, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.SPEAKING: {JarvisState.IDLE, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.PAUSED: {JarvisState.IDLE, JarvisState.ERROR, JarvisState.OFFLINE},
        JarvisState.ERROR: {JarvisState.IDLE, JarvisState.OFFLINE},
    }

    def __init__(
        self,
        initial_state: JarvisState = JarvisState.OFFLINE,
        event_bus: EventBus | None = None,
    ) -> None:
        self._current_state = initial_state
        self._event_bus = event_bus

    @property
    def current_state(self) -> JarvisState:
        """
        Return the current application state.
        """
        return self._current_state

    def transition(self, new_state: JarvisState) -> None:
        """
        Transition to a new state if valid.
        Raises InvalidStateTransitionError if the transition is not allowed.
        """
        if new_state == self._current_state:
            return

        allowed = self.ALLOWED_TRANSITIONS.get(self._current_state, set())
        # Allow transition to OFFLINE or ERROR from any state for safety during shutdown/exceptions
        if new_state not in allowed and new_state not in {JarvisState.OFFLINE, JarvisState.ERROR}:
            raise InvalidStateTransitionError(
                f"Invalid state transition from {self._current_state.name} to {new_state.name}"
            )

        old_state = self._current_state
        self._current_state = new_state

        if self._event_bus:
            self._event_bus.publish_type(
                EventType.STATE_CHANGED,
                {
                    "old_state": old_state,
                    "new_state": new_state,
                },
            )
