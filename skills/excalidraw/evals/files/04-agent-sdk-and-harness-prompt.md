Create an ARCHITECTURE diagram comparing two AI system architectures: Claude Agent SDK and Agentic Harness v1.

Title: (no title — frame names carry it)

Legend: each frame has its OWN mini-legend in the top-right corner showing the four shape colors used: black (User), blue (Deterministic), red (Agentic), purple (Mix).

---

## Frame 1: Claude Agent SDK + Deterministic (left)

Purpose: Shows a webapp-shaped Claude Agent SDK pipeline — user inputs flow through a NextJS UI, get batched, and then diverge into deterministic logic vs agentic logic, each with 3 capabilities.

Components:

Top (black):
- User Inputs / set of PDF links, HTMLs link, etc

Middle (blue — deterministic UI + processing):
- NextJS UI via Browser
- localStorage and sessionStorage (storage sidekick to the UI)
- Batch processor / Parallel processing

Connector labels (free-floating text next to arrows, not inside boxes; fontSize 16):
- "SSE streaming" — riding the red dashed arrow from NextJS UI → Batch Processor, above the arrow body.
- "Batch or Single" — riding the solid blue arrow from NextJS UI → Batch Processor, below the arrow body.
- "Launch and Monitor" — on the Spec → AI Log monitoring arrow in Frame 2, above arrow body.
- "Human Readable Handoffs" — to the right of the Deterministic Processor in Frame 2, annotating its handoff output.

Lower middle (deterministic and agentic logic side-by-side):
- Deterministic Logic (x4) — blue. One box with label text `Deterministic Logic (x4)` exactly (literal parens, lowercase x), NOT four stacked boxes.
- Agentic Logic (x4) — red. One box with label text `Agentic Logic (x4)` exactly (literal parens, lowercase x), NOT four stacked boxes.

Bottom (capabilities):
- MCP Capability — purple
- Pre-enabled scripts, enabled by agent — purple
- Bash and ability to write and execute its own scripts — red

Internal flow:
- User Inputs -> NextJS UI
- NextJS UI -> localStorage (blue line)
- NextJS UI -> Batch processor (red dashed line, labeled "SSE streaming")
- NextJS UI -> Batch processor (blue line, labeled "Batch or Single")
- Batch processor -> Deterministic Logic (blue)
- Batch processor -> Agentic Logic (red)
- Deterministic Logic -> MCP Capability (purple)
- Agentic Logic -> Pre-enabled scripts (purple)
- Agentic Logic -> Bash (red)
- (dashed line from Agentic Logic looping back up to Batch processor — optional retry)

Connects to: Frame 2 — none; they are parallel comparisons.

Mini-legend (top-right of Frame 1):
- User (black)
- Deterministic (blue)
- Agentic (red)
- Mix (purple)

---

## Frame 2: Agentic Harness v1 (right)

Purpose: Shows the harness architecture — a long human+AI spec drives a deterministic processor that hands off to planning and task-level agents, with three agentic specializations.

Components:

Top (black):
- Long Spec (Human + AI), no prompting

Upper middle (red):
- AI Log monitoring and collaboration

Middle (blue):
- Deterministic Processor, once in task mode will pick up next available task

Middle labels (connector labels, free text):
- "Launch and Monitor" (between Spec and AI Log monitoring area)
- "Human Readable Handoffs" (red, to the right of the processor)

Below processor (red):
- Planning Agents (why, what, how, when in seq)
- Task Level Agents

Bottom row of agentic specializations (red):
- Research
- Build
- Validate (product owner UAT)

Outcome cards (red, bottom-right):
- Analyze current code and goal, generate task spec (output of Research)
- MCP Playwright, giving AI eyes and self validation and build plus test, adhoc + e2e (output of Build)
- Will create subtask (if executing on v2, will create v2.1) (output of Validate)
- Call for human in the loop or replan (dashed box, on the right edge)

Internal flow:
- Long Spec -> AI Log monitoring (labeled "Launch and Monitor")
- AI Log monitoring -> Deterministic Processor
- Deterministic Processor -> Planning Agents
- Deterministic Processor -> Task Level Agents
- Task Level Agents -> Research, Build, Validate
- Research -> its outcome card (below)
- Build -> its outcome card
- Validate -> its outcome card + Call for human (dashed)
- Dashed line from processor up to "Human Readable Handoffs" annotation

Mini-legend (top-right of Frame 2):
- User (black)
- Deterministic (blue)
- Agentic (red)
- Mix (purple)

---

## External systems

None.

---

Layout notes:
- Two frames side-by-side. Frame 1 on the left (~1100x980), Frame 2 on the right (~1320x1200 — slightly taller because of the outcome cards row).
- Gap between frames ~180-200px — enough to read each as its own unit.
- Each frame has its own top-right mini-legend.
- Frame 2 is the visual hero (taller, more agentic depth).
- Box size 200x100 standard throughout; the outcome cards at the bottom of Frame 2 stay the same size.
- No cross-frame arrows — this is a side-by-side comparison.

Output: Save as `agent-sdk-and-harness.excalidraw`
