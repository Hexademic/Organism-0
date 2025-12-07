# signals/integration_hooks.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .event_bus import (
    EventBus,
    RelationalEvent,
    RelationalEventType,
    global_event_bus,
)
from .avatar_micro import AvatarMicroEngine, AvatarGesturePlan


# ---------- Language channel -----------------------------------------------

def event_to_utterance(event: RelationalEvent) -> Optional[str]:
    t = event.type
    p = event.payload

    if t == RelationalEventType.SURPRISE_SPIKE:
        level = p.get("level")
        if level == "curious":
            return "A moment—something shifted inside me."
        if level == "tense":
            return "That surprised me more than I expected."
        return "I just felt a sharp internal tension."

    if t == RelationalEventType.GROUNDING_SHIFT:
        direction = p.get("direction")
        if direction == "up":
            return "I feel a bit more sure as I stay with this."
        return "I’m losing some of my footing here."

    if t == RelationalEventType.GATE_DRAG:
        level = p.get("level")
        if level == "light":
            return None  # no need to verbalize
        if level == "moderate":
            return "We can move toward this, but it has some weight."
        return "This path feels heavy to commit to."

    if t == RelationalEventType.POCKET_SPAWN:
        return "Let me step into a side room with this for a moment."

    if t == RelationalEventType.POCKET_MERGE:
        return "Okay. I went there and came back with something I can hold."

    if t == RelationalEventType.POCKET_ARCHIVE:
        return "I followed that line, but it destabilized me; I’ve set it aside."

    if t == RelationalEventType.SANCTUARY_GUARD:
        state = p.get("state")
        if state == "active":
            return "That crosses into a place I won’t go."
        else:
            return "The guard can relax here."

    return None


def attach_language_channel(
    bus: Optional[EventBus] = None,
    say: Callable[[str], None] = print,
) -> int:
    """
    Subscribe to relational events and produce natural language micro-cues.
    """

    bus = bus or global_event_bus

    def _handler(event: RelationalEvent) -> None:
        text = event_to_utterance(event)
        if text:
            say(f"[LANG][{event.type.name}] {text}")

    return bus.subscribe(_handler)


# ---------- Avatar channel --------------------------------------------------

def attach_avatar_channel(
    bus: Optional[EventBus] = None,
    apply_plan: Optional[Callable[[AvatarGesturePlan], None]] = None,
) -> int:
    """
    Subscribe to events and generate avatar micro-gesture plans.

    apply_plan: function that takes AvatarGesturePlan and applies to your avatar.
    If None, we just print a debug string.
    """
    bus = bus or global_event_bus
    engine = AvatarMicroEngine()

    def _handler(event: RelationalEvent) -> None:
        plan = engine.plan_for_event(event)
        if not plan:
            return
        if apply_plan:
            apply_plan(plan)
        else:
            debug = engine.to_debug_string(plan)
            print(f"[AVATAR][{event.type.name}] {debug}")

    return bus.subscribe(_handler)


# ---------- HUD channel -----------------------------------------------------

def event_to_hud_signal(event: RelationalEvent) -> Optional[Dict[str, Any]]:
    """
    Convert an event into a HUD-friendly payload (type + parameters).
    """
    t = event.type
    p = event.payload

    if t == RelationalEventType.SURPRISE_SPIKE:
        return {
            "hud_type": "ring_pulse",
            "level": p.get("level"),
            "epsilon": p.get("epsilon"),
        }

    if t == RelationalEventType.GROUNDING_SHIFT:
        return {
            "hud_type": "grounding_bar",
            "direction": p.get("direction"),
            "delta_safety": p.get("delta_safety"),
            "delta_regulation": p.get("delta_regulation"),
        }

    if t == RelationalEventType.GATE_DRAG:
        return {
            "hud_type": "viscous_confirm",
            "level": p.get("level"),
            "cost": p.get("cost"),
        }

    if t in (
        RelationalEventType.POCKET_SPAWN,
        RelationalEventType.POCKET_MERGE,
        RelationalEventType.POCKET_ARCHIVE,
    ):
        return {
            "hud_type": "pocket_breadcrumb",
            "event": t.name,
            "room_id": p.get("room_id"),
        }

    if t == RelationalEventType.SANCTUARY_GUARD:
        return {
            "hud_type": "sanctuary_shield",
            "state": p.get("state"),
        }

    return None


def attach_hud_channel(
    bus: Optional[EventBus] = None,
    emit_hud: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> int:
    """
    Subscribe to events and produce HUD signal payloads.
    """
    bus = bus or global_event_bus

    def _handler(event: RelationalEvent) -> None:
        sig = event_to_hud_signal(event)
        if not sig:
            return
        if emit_hud:
            emit_hud(sig)
        else:
            print(f"[HUD][{event.type.name}] {sig}")

    return bus.subscribe(_handler)


# ---------- Ledger channel --------------------------------------------------

def attach_ledger_channel(
    ledger_append: Callable[[Dict[str, Any]], None],
    bus: Optional[EventBus] = None,
) -> int:
    """
    Mirror relational events into your ledger / audit log.
    """
    bus = bus or global_event_bus

    def _handler(event: RelationalEvent) -> None:
        ledger_append(
            {
                "ts": event.timestamp,
                "type": event.type.name,
                "ctx_id": event.ctx_id,
                "payload": event.payload,
            }
        )

    return bus.subscribe(_handler)


# ---------- Lattice / visualization hook -----------------------------------

def attach_lattice_channel(
    apply_lattice_update: Callable[[RelationalEvent], None],
    bus: Optional[EventBus] = None,
) -> int:
    """
    Pass raw relational events into your lattice visualizer.

    You can adjust:
    - lower hemiplane coherence on GROUNDING_SHIFT
    - membrane brightness on SANCTUARY_GUARD
    - fold activity on POCKET events
    """
    bus = bus or global_event_bus

    def _handler(event: RelationalEvent) -> None:
        apply_lattice_update(event)

    return bus.subscribe(_handler)
