Create a PROCESS diagram showing Jack's workflow evolution — manual prompting (before) vs the Agentic Harness v1 (after).

Title: (no title — frame names carry it)

Legend: none (single black color throughout).

---

## Summary / pre-frame

None — both frames stand on their own.

---

## Frame 1: How it was built (left)

Purpose: Describes Jack's personal workflow of 3-monitor manual build orchestration.

Components (tree-like, top to bottom):

Top:
- Me (central root at top)

Row 2 (3 children of "Me", left to right):
- ChatGPT Voice Brainstorming and Idealization
- Claude Refinement on why what how when
- Claude Code Long Running Build Orchestration

Row 3 (under Claude Code): Subagents for building (totally for 2 hours per batch)

Row 4 (convergence): All my inputs and results/action logged

Bottom (comparison cards):
- 5 months ago - 3 monitors manual build orchestration
- vs (free-floating text between the two cards)
- Now - Better AI life balance

Internal flow:
- Me -> each of the 3 children (fan-out)
- Claude Code Long Running Build Orchestration -> Subagents -> All inputs logged
- ChatGPT and Claude Refinement also feed into All inputs logged (convergence)
- Comparison cards sit at the bottom, not connected to the tree (just visual comparison)

Connects to: Frame 2 — no explicit cross-frame arrow.

---

## Frame 2: Agentic Harness v1 - How it was built (right)

Purpose: Describes the harness v1 that replaces the manual process — four input sources converge into Harness idealization, then a build cycle, optimization, and outcomes.

Components:

Top row (4 inputs, black, spread across the top):
- Spec Driven Development v1 + task master
- Claude Code Long Running Build Orchestration (reuses same concept as Frame 1)
- Spec Driven Development v2 with adhoc + test suite
- BMAD project / Spec Kit Project
- Subagent orchestration and context mgmt
- Years of consulting in CMS

(Combine into a row of 4 — or adjust to 6 small boxes if space allows; the canonical uses 6 small inputs spread across the top.)

Below inputs:
- Harness Idealization and concepting (central convergence point)

To the right of Harness Idealization:
- Requirements (free-floating multi-line text list): "1. 24 hour agentic feature to bug / 2. New or existing code base / 3. Human ..." (goes to ~5-6 lines)

Below Harness Idealization:
- Building and dev cycle

To the right of Building and dev cycle:
- Git Worktree - second vscode assess on going hand offs and runs, optimize
- Optimization - Iterative refinement via closed loop (similar to gradient dissent)

Below Building and dev cycle:
- Repeat and optimize, look at both the process and output

Bottom-right (annotation):
- Outcomes (free-floating multi-line text list): "1. While the first complete build didn't fail... / 2. Find iss with the process requirements..."

Internal flow:
- All 4-6 inputs fan IN to Harness Idealization
- Harness Idealization -> Building and dev cycle
- Building and dev cycle -> Git Worktree -> Optimization
- Building and dev cycle -> Repeat and optimize
- Repeat and optimize -> back up to Building and dev cycle (dashed loop — "repeat")

Connects to: Frame 1 — none.

---

## External systems

None.

---

Layout notes:
- Two frames side-by-side, Frame 1 on the left (~900x760), Frame 2 on the right (~1360x980).
- Frame 2 is wider and taller — the visual hero (the new system is the point).
- Gap between frames ~100-150px.
- Frame padding is tight (~20-40px L, wider bottom) because content is verbose.
- Inter-box rhythm stays ~100px.
- Multi-line free-floating text annotations (Requirements, Outcomes) sit inside frames as callouts; they are NOT inside rectangles.
- Cards at the bottom of Frame 1 (5 months ago, vs, Now) — same size as other boxes.

Output: Save as `prompts-to-harness.excalidraw`
