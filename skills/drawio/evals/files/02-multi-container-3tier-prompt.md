Create a 3-CONTAINER ARCHITECTURE diagram showing a robotics-style pipeline: raw sensor inputs are fused in a cognition core, which issues commands to an actuator mesh. The three containers sit side-by-side and exchange data through cross-frame edges.

**Three swimlane frames (side-by-side, left to right):**

### Frame 1 — Sensor Array (black border, `#1e1e1e`)
Components (standard 160–180 wide boxes, black stroke+font):
- Thermal Probe (IR + ambient)
- Optical Sensor
- Audio Mic Array
- Lidar Scan (32-beam)
- Vibration (**dashed** — optional capability)
- Sensor Health Monitor (blue, `#1971c2` — this one is Deterministic, not a sensor itself)

### Frame 2 — Cognition Core (black border)
Components (mixed colors — this is the brain):
- Signal Fusion (multi-modal) (**orange**, Mix — `#f08c00`)
- Pattern Matcher (**blue**, Deterministic — `#1971c2`)
- Intent Parser (LLM) (**red**, Agentic — `#e03131`)
- Context Synth (**orange**, Mix — `#f08c00`)
- Decision Tree (**blue**, Deterministic)
- Fail-safe Fallback (**blue**, Deterministic, **dashed** border)
- Explainer Log (black, default)

### Frame 3 — Actuator Mesh (black border)
Components:
- Motor Command Bus (black)
- Arm Servo Group (black)
- Tread Drive (black)
- Gripper Controller (black)
- LED/Audio Feedback (black, **dashed** — optional/noteworthy)
- Actuator Health Monitor (blue, Deterministic)

**Cross-frame edges (parent="1" — top-level, NOT inside any frame):**
- Sensor Health Monitor (F1) → Signal Fusion (F2) — blue edge, labeled "health stream" (italic)
- All five sensor boxes (F1) → Signal Fusion (F2) — black edges, **bus-pattern fan-in**: every edge must use `exitX=1;exitY=0.5` on the source AND `entryX=0` on Signal Fusion with entryY staggered across the sensors (e.g., entryY = 0.15, 0.3, 0.5, 0.7, 0.85 for the 5 sensors). The 5 arrows should arrive at Signal Fusion as parallel horizontal lines entering from its left side, NOT fanning in from multiple sides (octopus anti-pattern). They should be the same color and stroke width.
- Decision Tree (F2) → Motor Command Bus (F3) — blue edge, labeled "commands"
- Fail-safe Fallback (F2) → Motor Command Bus (F3) — blue **dashed** edge (feedback/fallback)
- Actuator Health Monitor (F3) → Explainer Log (F2) — black edge (reverse flow — diagnostics return)

**Intra-frame edges** (inside each frame — `parent="frame-id"`):
- F2: Signal Fusion → Pattern Matcher → Intent Parser → Context Synth → Decision Tree (linear pipeline vertically).
- F2: Decision Tree → Fail-safe Fallback (dashed, same-side left feedback loop — `exitX=0;exitY=0.5;entryX=0;entryY=0.5`).
- F2: Decision Tree → Explainer Log.
- F3: Motor Command Bus → Arm Servo Group / Tread Drive / Gripper Controller (fan-out).

**Legend** (4 labeled-pill swatches, 100×30) — place either inside Frame 2 top-right OR at top-left of the canvas outside any frame. Pick whichever reads cleanest given the 3-frame layout:
- User (`#1e1e1e`)
- Deterministic (`#1971c2`)
- Agentic (`#e03131`)
- Mix (`#f08c00`)

Layout notes:
- Three frames sit side-by-side. Frame 1 ~460 wide, Frame 2 ~560 wide (wider — more components), Frame 3 ~460 wide. All ~700 tall.
- 40–80px gap between adjacent frames — enough room for cross-frame edges to route cleanly.
- Coordinates snapped to 10px grid. Frame header (`startSize=30`) shows the title.
- All edges orthogonal (`edgeStyle=orthogonalEdgeStyle`, `rounded=0`, `strokeWidth=2`, `endArrow=classic`). Cross-frame edges use default routing; dashed fallback uses `dashed=1;dashPattern=8 8`.
- **Max 2 turns per edge.** If an edge needs more than 2 bends to reach its target, move the source or target box instead of hand-placing waypoints. No edge should have more than 2 `mxPoint` entries inside its `<Array as="points">`.
- **No edge may cross a non-endpoint box.** Trace every edge in the rendered PNG; if any edge's path passes through a box that is not its source or target, the layout is wrong — reposition a box and re-render.
- Every color-coded box must have MATCHING `strokeColor` AND `fontColor`. Never one without the other.

Output: Save as `multi-container-3tier.drawio`. Export to `multi-container-3tier.png` with the draw.io CLI (`-x -f png -b 10`, **no `-e`**).
