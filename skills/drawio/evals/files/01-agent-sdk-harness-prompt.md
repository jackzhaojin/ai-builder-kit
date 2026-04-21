Create an ARCHITECTURE diagram for the "Agentic Harness v1" — a single-subsystem view of how an agent-driven engineering harness turns a human-authored long spec into validated, task-level code changes.

Title of the swimlane: **Agentic Harness v1**

Components (labels can wrap onto 2 lines):
- Long Spec (Human + AI), no prompting (default/User — black)
- AI Log monitoring and collaboration (Agentic — red)
- Deterministic Processor, once in task mode will pick up next available task (Deterministic — blue)
- Planning Agents (why, what, how, when in seq) (Agentic — red)
- Task Level Agents (Agentic — red)
- Research (Agentic — red)
- Build (Agentic — red)
- Validate (product owner UAT) (Agentic — red)
- Call for human in the loop or replan (Agentic — red, **dashed border** — this is the indirect/noteworthy branch)
- Analyze current code and goal, generate task spec (Agentic — red)
- MCP Playwright, giving AI eyes and self validation and build plus test, adhoc + e2e regression (Agentic — red)
- Will create subtask (if executing on v2, will create v2.1) (Agentic — red)

Legend (inside the frame, top-right — 4 labeled-pill swatches):
- User (black, `#1e1e1e`)
- Deterministic (blue, `#1971c2`)
- Agentic (red, `#e03131`)
- Mix (orange, `#f08c00`)

Flow (top-to-bottom vertical):
1. **Long Spec → AI Log** (black edge)
2. **AI Log → Deterministic Processor** (red edge, labeled "Launch and Monitor" in italic red)
3. **Deterministic Processor → Task Level Agents** (blue edge, labeled "Human Readable Handoffs" in italic)
4. **Planning Agents → Deterministic Processor** (red **dashed** edge coming in from the left side — same-side left feedback loop, labeled "Human Readable Handoffs")
5. **Task Level Agents → Deterministic Processor** (red **dashed** right-side feedback loop, labeled "Human Readable Handoffs")
6. **Task Level Agents → Research** (red)
7. **Task Level Agents → Build** (red)
8. **Task Level Agents → Validate** (red)
9. **Validate → Call for human in the loop** (red, dashed recipient — the call-for-human box itself is dashed)
10. **Task Level Agents → Analyze current code** (red vertical)
11. **Analyze → MCP Playwright** (red)
12. **MCP Playwright → Will create subtask** (red)

Layout notes:
- Single swimlane frame with black border, 30px header, rounded=0 on the frame.
- Frame sized approximately 920 × 820.
- Grid snap at 10px. Standard box widths 120–180, heights 50–80. Legend swatches 100×30, fontSize 12, 40px vertical spacing, positioned top-right inside the frame.
- Orthogonal edges (`edgeStyle=orthogonalEdgeStyle`, `rounded=0`).
- Dashed edges use `dashed=1;dashPattern=8 8`.
- Feedback loops use **same-side** exit/entry (both left OR both right; `exitX=0;exitY=0.5;entryX=0;entryY=0.5` or the right-side equivalent).
- Edge labels that carry text (Launch and Monitor, Human Readable Handoffs) are italic HTML spans; they live as child `mxCell` nodes of the edge with `edgeLabel` style and `parent="edge-id"`.

Output: Save as `agent-sdk-harness.drawio`. Export to `agent-sdk-harness.png` with the draw.io CLI (`-x -f png -b 10`, **no `-e`**).
