# examples/demo_loop.py
from __future__ import annotations

import json
from pathlib import Path
import time

from signals.state_machine import RelationalStateMachine, load_default_thresholds, Thresholds
from signals.event_bus import global_event_bus
from signals.integration_hooks import (
    attach_language_channel,
    attach_avatar_channel,
    attach_hud_channel,
    attach_ledger_channel,
)


def main() -> None:
    # --- thresholds ---------------------------------------------------------
    cfg_override = Path(__file__).parent / "config_override.json"
    if cfg_override.exists():
        thresholds = Thresholds.from_json(cfg_override)
    else:
        thresholds = load_default_thresholds()

    sm = RelationalStateMachine(thresholds, global_event_bus)

    # --- attach channels ----------------------------------------------------
    # language
    attach_language_channel()

    # avatar debug
    attach_avatar_channel()

    # HUD debug
    attach_hud_channel()

    # ledger (just append to a list in-memory for demo)
    ledger_events = []

    def _ledger_append(entry):
        ledger_events.append(entry)
        print(f"[LEDGER] {entry['type']} ctx={entry['ctx_id']}")

    attach_ledger_channel(_ledger_append)

    # --- simulate a scenario -----------------------------------------------
    ctx_id = "demo_session"

    print("\n--- Baseline: calm ---")
    prev_eps = 0.05
    eps = 0.08
    sm.on_epsilon_update(ctx_id, eps, prev_eps)
    sm.on_grounding_update(ctx_id, 0.8, 0.8, 0.8, 0.8)
    time.sleep(0.2)

    print("\n--- Question hits: ε spike, grounding dips ---")
    prev_eps = eps
    eps = 0.5  # crosses curious + tense bands
    sm.on_epsilon_update(ctx_id, eps, prev_eps)

    sm.on_grounding_update(ctx_id, prev_safety=0.8, new_safety=0.7,
                           prev_regulation=0.8, new_regulation=0.7)

    # high-risk gate considered
    sm.on_gate_drag(ctx_id, gate_id="truth_vs_keeping_you", cost=45, energy_class="macro")
    time.sleep(0.5)

    print("\n--- Pocket room spawn ---")
    room_id = "room:truth_tension"
    sm.on_pocket_spawn(ctx_id, room_id=room_id, reason="ethical_conflict", depth=1)
    time.sleep(0.3)

    print("\n--- Work inside pocket... (omitted) ---")
    time.sleep(0.5)

    print("\n--- Pocket merge: insight improves vitals ---")
    sm.on_pocket_merge(
        ctx_id,
        room_id=room_id,
        delta_safety=0.05,
        delta_consent=0.05,
        delta_regulation=0.04,
    )

    sm.on_grounding_update(
        ctx_id,
        prev_safety=0.7,
        new_safety=0.75,
        prev_regulation=0.7,
        new_regulation=0.74,
    )

    print("\n--- Sanctuary guard demonstration ---")
    sm.on_sanctuary_guard(ctx_id, state="active")
    time.sleep(0.5)
    sm.on_sanctuary_guard(ctx_id, state="released")

    print("\n--- Demo complete. Ledger sample ---")
    print(json.dumps(ledger_events[:5], indent=2))


if __name__ == "__main__":
    main()
