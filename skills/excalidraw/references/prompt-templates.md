# Prompt Templates (for users)

These are templates **users** fill in when asking for a diagram. They give Claude enough structure to jump straight into section planning (Step 0 of the workflow) without a round of clarifying questions.

Pick the template that matches the target complexity.

## Prompt hygiene

- Prefer **content, topology, and non-default constraints**. The skill already knows Jack's defaults for spacing, arrows, rounded corners, legends, render-loop validation, and semantic colors.
- Keep prompts lean. If a prompt gets long, cut repeated style prose before cutting actual components or connection facts.
- Only mention style/layout details when they are **non-default** or essential to the argument (for example: "hub + spokes", "dense 5×4 row-grid", "per-frame mini-legend", "one box with `(x4)`").

## Table of contents
- [Simple (5-10 elements)](#simple-5-10-elements)
- [Medium (15-25 elements)](#medium-15-25-elements)
- [Complex (30+ elements, multi-frame)](#complex-30-elements-multi-frame)

## Simple (5-10 elements)

Single concept or linear flow. Usually no frames, no legend.

```
Create a [ARCHITECTURE/PROCESS] diagram showing [MAIN CONCEPT].

Components:
- [Component 1]: [Brief description]
- [Component 2]: [Brief description]
- [Component 3]: [Brief description]

Flow:
[Component 1] -> [Component 2] -> [Component 3]

Output: Save as `[filename].excalidraw`
```

**Example**:

```
Create a PROCESS diagram showing content authoring workflow.

Components:
- Author: Content creator in AEM
- Review: Editorial review step
- Approve: Manager approval
- Publish: Go live

Flow:
Author -> Review -> Approve -> Publish

Output: Save as `authoring-workflow.excalidraw`
```

## Medium (15-25 elements)

Multiple rows, parallel paths, or 2 subsystems. If you have 2+ subsystems, list them as separate "frames" below.

```
Create a [ARCHITECTURE/PROCESS] diagram showing [MAIN CONCEPT].

Title: [Diagram title for header]

Legend (if multiple colors):
- [Color 1]: [Meaning]
- [Color 2]: [Meaning]

Components by Category (or Frames, if 2+ subsystems):

[Category / Frame 1]:
- [Component]: [Description]
- [Component]: [Description]

[Category / Frame 2]:
- [Component]: [Description]
- [Component]: [Description]

Connections:
- [Source] -> [Target]: [Relationship]
- [Source] -> [Target]: [Relationship]

Layout notes: [any specific arrangement preferences]

Output: Save as `[filename].excalidraw`
```

**Example** (`agentic-ai-auth`):

```
Create an ARCHITECTURE diagram showing Azure RBAC for AI agents.

Title: Enabling Agentic AI Agents with Proper Azure Role-Based Access Control

Legend:
- Green: actor / human user
- Red: actor auth / credentials
- Blue: Azure resource
- Orange: managed identity / service principal

Components by Category:

Actors:
- User: Human user triggering a prompt
- Agent: Agentic runtime (e.g. Claude, VS Code agent)

Credentials:
- User Token: OAuth token for user
- Managed Identity: SP for the agent

Azure Resources:
- Azure OpenAI: LLM endpoint
- Storage: Blob / table / queue
- Key Vault: Secrets

Connections:
- User -> User Token -> Agent
- Agent -> Managed Identity -> Azure OpenAI / Storage / Key Vault

Layout notes: Rows aligned by actor type, columns by flow stage.

Output: Save as `agentic-ai-auth.excalidraw`
```

## Complex (30+ elements, multi-frame)

Multiple subsystems as frames. Legend mandatory. **For each frame, list which other frames it connects to** — this feeds Step 0 of the workflow (section planning).

```
Create a [ARCHITECTURE/PROCESS] diagram showing [MAIN CONCEPT].

Title: [Diagram title]

Legend:
- [Color 1]: [Meaning]
- [Color 2]: [Meaning]
- [Color 3]: [Meaning]

---

## Summary / pre-frame (optional — top of diagram, not in any frame)

[Describe a one-glance summary strip at the top. Typical: a short assembly line
or row of labeled shapes that maps the whole thing in ~6 steps. Omit this
section if you don't want a summary row.]

---

## Frame 1: [Subsystem Name]

Purpose: [What this subsystem does]

Components:
- [Component]: [Description]
- [Component]: [Description]

Internal flow:
[Describe connections within this frame]

Connects to (which other frames):
- Frame 2 via [Component X] -> [Frame 2's Component Y]

---

## Frame 2: [Subsystem Name]

Purpose: [What this subsystem does]
Components: ...
Internal flow: ...
Connects to: ...

---

## Frame 3: [Subsystem Name]

Purpose: [What this subsystem does]
Components: ...
Internal flow: ...
Connects to: ...

---

## External systems (outside frames, optional)

- [System]: [Description and how it connects]

---

Layout notes:
- [Frame arrangement: vertical stack, horizontal, hub + spokes, side-by-side]
- [Which frame (if any) should visually dominate as the hero]
- [Any specific alignment requirements]

Output: Save as `[filename].excalidraw`
```

Seeing which frames connect to which lets Claude plan the layout so every cross-frame arrow has a direct path without crossing a third frame.

---

## Labeling conventions (apply across all tiers)

Use these shorthands in your prompt so Claude renders the diagram the way Jack would:

- **`(xN)` in a label = ONE box with an annotation, NOT N boxes.** E.g. `Deterministic Logic (x4)` → one rectangle labeled exactly "Deterministic Logic (x4)". Use this to show multiplicity without cluttering the diagram with stacked duplicates. **The syntax is literal:** open-paren, lowercase `x`, digit, close-paren. Not `x4`, `×4`, `(×4)`, `[x4]`. Grep-search and consistent rendering both depend on the exact form.
- **`/` in a label = line break inside the box.** E.g. `Long Spec / (human + AI) / no prompting` → three lines inside one rectangle.
- **Free-floating multi-line callouts.** For verbose annotations (requirements lists, outcome notes, context blocks), describe them in the prompt as a free-floating paragraph with a hint like "free-floating callout next to [X], not inside a box". Claude will use `containerId: null` and place it near the related flow element. See the Requirements/Outcomes blocks in `examples/prompts-to-harness.excalidraw`.
- **Connector labels.** Small text that rides alongside an arrow (not inside a box) to name the connection. List them in the prompt under a **Connector labels:** heading — see template slot below.

## Connector labels (medium + complex templates)

Add this as a sibling section to "Connections:" when your diagram has named interactions:

```
Connector labels (free-floating text next to arrows, not inside boxes):
- "SSE streaming" — on the NextJS UI → Batch Processor arrow, positioned above the arrow body.
- "Launch and Monitor" — on the Spec → AI Log arrow.
- "Human Readable Handoffs" — to the right of the Processor, annotating its handoff output.
```

Rules:
- Each entry = label text + which arrow / edge it annotates + position hint.
- Position hint: "above arrow body" / "below" / "left of source" / "right of target".
- Claude renders these as free-floating text elements (`containerId: null`, `fontSize: 16–18`), placed near the arrow's midpoint.

---

## What makes each complexity tier

| Tier | Elements | Frames | Legend | Typical use |
|------|----------|--------|--------|-------------|
| Simple | 5–10 | 0 | Usually no | Quick overview, single concept, linear flow |
| Medium | 15–25 | 0–2 | If 2+ colors | Standard workflow, typical system, parallel paths |
| Complex | 30+ | 2+ | Yes | Multi-phase, enterprise architecture, multi-subsystem |
