Create an ARCHITECTURE diagram showing the Summit 2026 demo architecture — a content-delivery hub with three orbiting subsystems that feed and consume content.

Title: (no title — frame names carry it)

Legend: none at top level. Frame 3 ("Evals Container") has its own mini-legend in its top-right.

---

## Summary / pre-frame

None. The hub-and-spokes layout IS the summary.

---

## Central hub (outside all frames)

- da.live EDS site (large black rectangle in the canvas center — the hub)

---

## Frame 1: Mock Content Input Generation (top-left, feeds the hub)

Purpose: Generates mock content (PDFs and HTML) via the Claude Agent SDK and stores it in Azure, then pushes to da.live.

Components:

Top:
- Spec (Human + AI), no prompting (black)

Top-right (red):
- Claude Agent SDK

Middle (red, two outputs):
- PDFs
- HTML

Bottom (red):
- Azure Storage Account (for WF Fusion and Evals)

Internal flow:
- Spec -> Claude Agent SDK
- Claude Agent SDK -> PDFs
- Claude Agent SDK -> HTML
- PDFs / HTML -> Azure Storage Account (convergence)

Connects to: Hub — arrow from Azure Storage Account to the central "da.live EDS site".

---

## Frame 2: Content Builder - Workfront Fusion / Make.com (bottom-left, feeds the hub)

Purpose: Shows the Workfront Fusion / Make.com agent pipeline that pulls foundational models, context memory, and MCP tools to build content.

Components:

Top (black):
- Trigger with param
- Agent (to the right of trigger)

Below Agent, three columns (black):
- Foundational Models (column 1)
- Context / Memory / Block Content Library / Sample pages / Lessons learned (column 2, multi-line stack)
- MCP Servers / Tools (column 3 header)
  - Playwright (under MCP Servers)
  - AEM da.live GET / UPDATE / CREATE / PUBLISH (under MCP Servers)

Internal flow:
- Trigger -> Agent
- Agent -> Foundational Models, Context / Memory, MCP Servers (fan-out)
- MCP Servers -> Playwright
- MCP Servers -> AEM da.live commands

Connects to: Hub — arrow from Agent (or MCP Servers row) to central "da.live EDS site".

---

## Frame 3: Evals Container Deployed on Oracle VM (right, consumes content from the hub)

Purpose: The evals container that ingests published content from da.live to run batch processing with deterministic + agentic logic.

This frame reuses the same internal structure as the agent-sdk-and-harness Frame 1.

Mini-legend (top-right of Frame 3):
- User (black)
- Deterministic (blue)
- Agentic (red)
- Mix (purple)

Components:
- User Inputs / set of PDF links, HTMLs link, etc (black, top)
- NextJS UI via Browser (blue)
- localStorage and sessionStorage (blue sidekick, right of UI)
- Batch processor / Parallel processing (blue, labels "SSE streaming" + "Batch or Single")
- Deterministic Logic (x4) (blue) — one box with label text `Deterministic Logic (x4)` exactly (literal parens, lowercase x), NOT four stacked boxes.
- Agentic Logic (x4) (red) — one box with label text `Agentic Logic (x4)` exactly (literal parens, lowercase x), NOT four stacked boxes.
- MCP Capability (purple)
- Pre-enabled scripts, enabled by agent (purple)
- Bash and ability to write and execute its own scripts (red)

Internal flow: same as agent-sdk-and-harness Frame 1 (see 04-agent-sdk-and-harness-prompt.md).

Connects to: Hub — arrow from central "da.live EDS site" into User Inputs (this frame consumes from the hub).

---

## External systems

None.

---

Layout notes:
- Hub-and-spokes. Central shape: "da.live EDS site" in the middle of canvas.
- Frame 1 (Mock Content Input) positioned top-left, arrow pointing right-down to the hub.
- Frame 2 (Content Builder) positioned bottom-left, arrow pointing right-up to the hub.
- Frame 3 (Evals Container) positioned to the right of the hub, arrow from hub pointing right into this frame.
- Frames surround the hub with ~200-400px gap between each frame's edge and the hub.
- Each frame's arrow to the hub uses the hub's orbit binding (mode: "orbit") so arrows distribute cleanly around the hub's edges.

Output: Save as `summit-2026-v2-simple.excalidraw`
