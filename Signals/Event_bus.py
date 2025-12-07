# signals/event_bus.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional
import time


class RelationalEventType(Enum):
    SURPRISE_SPIKE = auto()
    GROUNDING_SHIFT = auto()
    GATE_DRAG = auto()
    POCKET_SPAWN = auto()
    POCKET_MERGE = auto()
    POCKET_ARCHIVE = auto()
    SANCTUARY_GUARD = auto()


@dataclass
class RelationalEvent:
    """
    Canonical event flowing through all modalities.
    One truth → many expressions.
    """
    type: RelationalEventType
    timestamp: float
    ctx_id: str
    payload: Dict[str, Any]


Subscriber = Callable[[RelationalEvent], None]


class EventBus:
    """
    Simple pub/sub bus for relational events.

    - subscribe(callback, event_types=None) -> token
    - unsubscribe(token)
    - publish(event)
    """

    def __init__(self) -> None:
        self._subscribers: Dict[int, Dict[str, Any]] = {}
        self._next_token: int = 1

    def subscribe(
        self,
        callback: Subscriber,
        event_types: Optional[List[RelationalEventType]] = None,
    ) -> int:
        token = self._next_token
        self._next_token += 1
        self._subscribers[token] = {
            "callback": callback,
            "event_types": set(event_types) if event_types else None,
        }
        return token

    def unsubscribe(self, token: int) -> None:
        self._subscribers.pop(token, None)

    def publish(self, event: RelationalEvent) -> None:
        # Simple synchronous fan-out; you can swap to async later if needed.
        for sub in self._subscribers.values():
            allowed = sub["event_types"]
            if allowed is None or event.type in allowed:
                sub["callback"](event)


# Global singleton (you can also instantiate your own)
global_event_bus = EventBus()


def now_ts() -> float:
    return time.time()
