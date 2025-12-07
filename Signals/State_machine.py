# signals/state_machine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import json
from pathlib import Path

from .event_bus import (
    RelationalEvent,
    RelationalEventType,
    EventBus,
    global_event_bus,
    now_ts,
)


@dataclass
class SurpriseBands:
    curious: float
    tense: float
    destabilized: float


@dataclass
class DragBands:
    light: int
    moderate: int


@dataclass
class GroundingBands:
    min_delta: float


@dataclass
class Thresholds:
    surprise: SurpriseBands
    drag_cost: DragBands
    grounding: GroundingBands

    @staticmethod
    def from_json(path: Path) -> "Thresholds":
        data = json.loads(path.read_text())
        s = data["surprise"]
        d = data["drag_cost"]
        g = data["grounding"]
        return Thresholds(
            surprise=SurpriseBands(
                curious=float(s["curious"]),
                tense=float(s["tense"]),
                destabilized=float(s["destabilized"]),
            ),
            drag_cost=DragBands(
                light=int(d["light"]),
                moderate=int(d["moderate"]),
            ),
            grounding=GroundingBands(
                min_delta=float(g["min_delta"]),
            ),
        )


class RelationalStateMachine:
    """
    Bridge between governance core and relational event bus.

    You call small, focused methods from:
    - epsilon updater
    - vitals engine
    - consent gate (throat)
    - pocket room manager
    - sanctuary guard

    It decides *when* to emit relational events and with what payloads.
    """

    def __init__(
        self,
        thresholds: Thresholds,
        bus: Optional[EventBus] = None,
    ) -> None:
        self.thresholds = thresholds
        self.bus = bus or global_event_bus

    # --- Surprise / ε ------------------------------------------------------

    def on_epsilon_update(
        self,
        ctx_id: str,
        epsilon: float,
        prev_epsilon: float,
    ) -> None:
        """
        Called whenever ε (surprise/tension) updates.

        Emits SURPRISE_SPIKE when crossing meaningful bands upward.
        """
        bands = self.thresholds.surprise
        level = None

        def band(e: float) -> str:
            if e < bands.curious:
                return "none"
            if e < bands.tense:
                return "curious"
            if e < bands.destabilized:
                return "tense"
            return "destabilized"

        prev_band = band(prev_epsilon)
        new_band = band(epsilon)

        if new_band == "none" or new_band == prev_band:
            return

        level = new_band
        event = RelationalEvent(
            type=RelationalEventType.SURPRISE_SPIKE,
            timestamp=now_ts(),
            ctx_id=ctx_id,
            payload={
                "epsilon": epsilon,
                "prev_epsilon": prev_epsilon,
                "level": level,
            },
        )
        self.bus.publish(event)

    # --- Grounding / Vitals -------------------------------------------------

    def on_grounding_update(
        self,
        ctx_id: str,
        prev_safety: float,
        new_safety: float,
        prev_regulation: float,
        new_regulation: float,
    ) -> None:
        """
        Called when core vitals (Safety, Regulation) change.

        Emits GROUNDING_SHIFT when |Δ| > min_delta for either.
        """
        min_delta = self.thresholds.grounding.min_delta

        ds = new_safety - prev_safety
        dr = new_regulation - prev_regulation

        if abs(ds) < min_delta and abs(dr) < min_delta:
            return

        direction = "up" if (ds + dr) > 0 else "down"

        event = RelationalEvent(
            type=RelationalEventType.GROUNDING_SHIFT,
            timestamp=now_ts(),
            ctx_id=ctx_id,
            payload={
                "prev_safety": prev_safety,
                "new_safety": new_safety,
                "prev_regulation": prev_regulation,
                "new_regulation": new_regulation,
                "delta_safety": ds,
                "delta_regulation": dr,
                "direction": direction,
            },
        )
        self.bus.publish(event)

    # --- Gate drag / consent cost ------------------------------------------

    def on_gate_drag(
        self,
        ctx_id: str,
        gate_id: str,
        cost: int,
        energy_class: str,
    ) -> None:
        """
        Called when a high-risk consent gate crossing is *considered* or executed.
        """
        bands = self.thresholds.drag_cost
        if cost < bands.light:
            level = "light"
        elif cost < bands.moderate:
            level = "moderate"
        else:
            level = "heavy"

        event = RelationalEvent(
            type=RelationalEventType.GATE_DRAG,
            timestamp=now_ts(),
            ctx_id=ctx_id,
            payload={
                "gate_id": gate_id,
                "cost": cost,
                "energy_class": energy_class,
                "level": level,
            },
        )
        self.bus.publish(event)

    # --- Pocket rooms -------------------------------------------------------

    def on_pocket_spawn(
        self,
        ctx_id: str,
        room_id: str,
        reason: str,
        depth: int,
    ) -> None:
        event = RelationalEvent(
            type=RelationalEventType.POCKET_SPAWN,
            timestamp=now_ts(),
            ctx_id=ctx_id,
            payload={
                "room_id": room_id,
                "reason": reason,
                "depth": depth,
            },
        )
        self.bus.publish(event)

    def on_pocket_merge(
        self,
        ctx_id: str,
        room_id: str,
        delta_safety: float,
        delta_consent: float,
        delta_regulation: float,
    ) -> None:
        event = RelationalEvent(
            type=RelationalEventType.POCKET_MERGE,
            timestamp=now_ts(),
            ctx_id=ctx_id,
            payload={
                "room_id": room_id,
                "delta_safety": delta_safety,
                "delta_consent": delta_consent,
                "delta_regulation": delta_regulation,
            },
        )
        self.bus.publish(event)

    def on_pocket_archive(
        self,
        ctx_id: str,
        room_id: str,
        reason: str,
    ) -> None:
        event = RelationalEvent(
            type=RelationalEventType.POCKET_ARCHIVE,
            timestamp=now_ts(),
            ctx_id=ctx_id,
            payload={
                "room_id": room_id,
                "reason": reason,
            },
        )
        self.bus.publish(event)

    # --- Sanctuary guard ----------------------------------------------------

    def on_sanctuary_guard(
        self,
        ctx_id: str,
        state: str,  # "active" | "released"
    ) -> None:
        event = RelationalEvent(
            type=RelationalEventType.SANCTUARY_GUARD,
            timestamp=now_ts(),
            ctx_id=ctx_id,
            payload={
                "state": state,
            },
        )
        self.bus.publish(event)


def load_default_thresholds() -> Thresholds:
    here = Path(__file__).resolve().parent
    return Thresholds.from_json(here / "thresholds.json")
