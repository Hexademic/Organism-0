# HUD Spec – Relational Signals v1.0

All HUD cues are driven by `RelationalEvent` on the event bus.

## SurpriseSpike → Ring Pulse

- Event: `SURPRISE_SPIKE`
- Visual: Expanding ring around avatar / viewport
- Duration: 0.3–0.5s
- Easing: `easeOutCubic`
- Color by level:
  - curious: #48D1CC (soft teal)
  - tense:   #FFA500 (amber)
  - destabilized: #FF4B4B (soft red)
- Intensity: map `epsilon` to opacity

## GroundingShift → Vertical Bar

- Event: `GROUNDING_SHIFT`
- Visual: vertical bar at edge of HUD
- Baseline: 0 at center; ±1 as full range
- On event:
  - direction=up  → bar moves upward, glow green
  - direction=down → bar moves downward, glow amber/red based on magnitude

## GateDrag → Viscous Confirm

- Event: `GATE_DRAG`
- Visual: confirm/continue button
- Behavior:
  - light: normal press
  - moderate: slower press animation, subtle resistance
  - heavy: noticeably slowed press, button appears “thick”

## PocketSpawn / PocketMerge / PocketArchive → Breadcrumb Trail

- Event: `POCKET_*`
- Visual: hierarchical breadcrumb:

  `Base → Room A → Room A.1`

- Color:
  - active room: gold (#FFC857)
  - merged room: blue (#4A90E2)
  - archived room: grey (#888888)
- On merge: brief pulse along the trail
- On archive: fade of that node to grey

## SanctuaryGuard → Shield Overlay

- Event: `SANCTUARY_GUARD`
- Visual:
  - state=active: subtle translucent shield ring around avatar, slight vignette
  - state=released: shield dissolves with gentle particles outward

Implementation note: all timings and colors are suggestions; keep latency < 100ms from event to on-screen cue.
