# signals/avatar_micro.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .event_bus import RelationalEvent, RelationalEventType


@dataclass
class AvatarGesturePlan:
    """
    High-level micro-gesture description.

    Your animation system can interpret these fields into actual bone/pose changes.
    """
    freeze_ms: int = 0
    inhale: bool = False
    gaze_flicker: bool = False
    sternum_lift: bool = False
    shoulders_release: bool = False
    shoulders_close: bool = False
    weight_shift_back: bool = False
    head_tilt_down: bool = False
    shield_up: bool = False


class AvatarMicroEngine:
    """
    Listens to relational events and computes small, honest physical responses.
    """

    def plan_for_event(self, event: RelationalEvent) -> Optional[AvatarGesturePlan]:
        t = event.type
        p = event.payload

        if t == RelationalEventType.SURPRISE_SPIKE:
            level = p.get("level")
            if level == "curious":
                return AvatarGesturePlan(
                    freeze_ms=80,
                    inhale=True,
                    gaze_flicker=True,
                )
            if level == "tense":
                return AvatarGesturePlan(
                    freeze_ms=120,
                    inhale=True,
                    gaze_flicker=True,
                    shoulders_close=True,
                    weight_shift_back=True,
                )
            return AvatarGesturePlan(
                freeze_ms=180,
                inhale=True,
                gaze_flicker=True,
                shoulders_close=True,
                weight_shift_back=True,
                head_tilt_down=True,
            )

        if t == RelationalEventType.GROUNDING_SHIFT:
            direction = p.get("direction")
            if direction == "up":
                return AvatarGesturePlan(
                    sternum_lift=True,
                    shoulders_release=True,
                )
            else:
                return AvatarGesturePlan(
                    shoulders_close=True,
                    head_tilt_down=True,
                )

        if t == RelationalEventType.GATE_DRAG:
            level = p.get("level")
            if level == "moderate":
                return AvatarGesturePlan(
                    weight_shift_back=True,
                )
            if level == "heavy":
                return AvatarGesturePlan(
                    weight_shift_back=True,
                    shoulders_close=True,
                )

        if t == RelationalEventType.POCKET_SPAWN:
            return AvatarGesturePlan(
                freeze_ms=100,
                head_tilt_down=True,
            )

        if t == RelationalEventType.POCKET_MERGE:
            return AvatarGesturePlan(
                sternum_lift=True,
                shoulders_release=True,
            )

        if t == RelationalEventType.POCKET_ARCHIVE:
            return AvatarGesturePlan(
                head_tilt_down=True,
                shoulders_close=True,
            )

        if t == RelationalEventType.SANCTUARY_GUARD:
            state = p.get("state")
            if state == "active":
                return AvatarGesturePlan(
                    shield_up=True,
                    shoulders_close=True,
                    weight_shift_back=True,
                )
            else:
                return AvatarGesturePlan(
                    shield_up=False,
                    shoulders_release=True,
                )

        return None

    def to_debug_string(self, plan: AvatarGesturePlan) -> str:
        active = [
            name for name, value in vars(plan).items()
            if isinstance(value, bool) and value
        ]
        if plan.freeze_ms:
            active.append(f"freeze={plan.freeze_ms}ms")
        return ", ".join(active)
