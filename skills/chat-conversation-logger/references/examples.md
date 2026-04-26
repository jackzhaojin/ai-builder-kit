# Worked Examples

Two end-to-end example logs, fictional but realistic. Both are complete files — frontmatter, headers, prompt blocks, the works. Use them as a reference when you're unsure how a real log should look.

---

## Example 1: Short, clean Q&A session

**Filename:** `2026-04-15-1102-pkce-vs-auth-code-flow-comparison.md`

```markdown
---
date: 2026-04-15
time: "11:02"
platform: claude-ai
model: claude-opus-4-7
topic: pkce-vs-auth-code-flow-comparison
tags: [oauth, ciam, security, identity]
prompt_count: 3
status: complete
---

# PKCE vs Auth Code Flow Comparison — Conversation Log

**Date**: 2026-04-15 11:02
**Platform**: Claude.ai
**Topic**: Quick clarification on when to use PKCE vs traditional auth code flow for a SPA-plus-BFF architecture.

---

## Session: PKCE vs auth code flow

### Prompt 1: Initial framing

**Inputs**: text only

> hey can you remind me when i should be using PKCE vs traditional authorization code flow? im doing a SPA with a BFF in front of it, and the BFF holds the refresh token. i think i still need PKCE on the front channel even though the BFF is the actual confidential client?

→ Response: Confirmed — PKCE protects the front-channel auth code from interception even when the back-end is a confidential client; the two layers protect different attack surfaces.
→ Action: Walked through the threat model in three short paragraphs, no diagrams needed.
→ Tools: none

---

### Prompt 2: Edge case on token storage

**Inputs**: text only

> ok so if the BFF holds the refresh token, what about the access token? same place, or do i pass it to the SPA via a session cookie?

→ Response: Recommended keeping the access token in the BFF as well and using an HTTP-only session cookie between SPA and BFF — keeps tokens out of JS-accessible storage.
→ Action: Sketched the request flow (browser → BFF cookie session → BFF attaches Bearer → upstream API).
→ Tools: none

---

### Prompt 3: Sanity check against Adobe IMS

**Inputs**: text only

> does adobe IMS support PKCE? i thought i remembered them being a holdout

→ Response: Adobe IMS supports PKCE for public clients — confirmed via current docs.
→ Action: Pulled the relevant section of the Adobe IMS OAuth docs.
→ Tools: web_search, web_fetch

---

<!--
  Trigger prompt ("/log this") not logged per skill rule.
-->
```

---

## Example 2: Long, tool-heavy build session

**Filename:** `2026-04-22-2014-cea-priority-queue-dashboard-build.md`

```markdown
---
date: 2026-04-22
time: "20:14"
platform: claude-ai
model: claude-opus-4-7
topic: cea-priority-queue-dashboard-build
tags: [agentic-ai, dashboard, react, continuous-executive-agent]
prompt_count: 9
status: in-progress
---

# CEA Priority Queue Dashboard Build — Conversation Log

**Date**: 2026-04-22 20:14
**Platform**: Claude.ai
**Topic**: First-pass dashboard for the Continuous Executive Agent priority queue, showing goal/step/contract hierarchy with live worker status.

---

## Session: Dashboard mockup and iteration

### Prompt 1: Initial spec

**Inputs**: text + 1 image (whiteboard photo of queue layout sketch)

> ok here's the rough sketch i drew on the whiteboard tonight. need a dashboard for the CEA priority queue. left rail = goals, middle = active steps, right rail = worker pool with status. each worker shows model vendor (claude/codex/kimi) and what its currently grinding on. clicking a step shows the contract. dark mode obviously.

📎 *Attachment: whiteboard-cea-queue-sketch.jpg — three-column layout, hand-drawn*

→ Response: Confirmed the three-column layout, asked about live update mechanism (poll vs WebSocket) before drafting.
→ Action: No artifact yet, gathering spec.
→ Tools: none

---

### Prompt 2: Live update decision

**Inputs**: text only

> poll every 2s is fine for now, can swap to websocket later. and yeah dark mode primary, light mode can come later

→ Response: Locked spec. Drafted React component with three columns, mock data for 4 goals / 7 steps / 3 workers.
→ Action: Rendered v1 artifact with Tailwind dark mode, recharts for the worker utilization sparkline. ✅
→ Tools: visualize:show_widget

---

### Prompt 3: Worker status colors

**Inputs**: text only

> the worker status colors are kinda meh. green/yellow/red is fine for traffic light but can we do something more like the agent SDK telemetry — idle is dim, working is a slow pulse, blocked is a hard red border?

→ Response: Agreed, traffic-light is overused. Implemented dim/pulse/red-border treatment.
→ Action: Updated artifact with CSS animation for the working pulse (2s ease-in-out), kept blocked state high-contrast. ✅
→ Tools: visualize:show_widget

---

### Prompt 4: Contract panel

**Inputs**: text only

> clicking a step should slide out a contract panel from the right. show the contract JSON, but pretty-printed and with the key fields highlighted (goal_id, step_id, vendor, model, max_tokens, deadline)

→ Response: Built slide-out panel with syntax-highlighted JSON, key fields bolded.
→ Action: Used a small custom highlighter (no library) to keep the artifact self-contained. ✅
→ Tools: visualize:show_widget

---

### Prompt 5: Mock data realism

**Inputs**: text + pasted code (TypeScript, ~80 lines — the user's Goal/Step/Contract type definitions)

> here are the actual TS types from the harness, can you make the mock data conform to these instead of whatever you made up

📎 *Pasted code: TypeScript interfaces for Goal, Step, Contract, WorkerStatus from the CEA codebase*

→ Response: Replaced mock data with conformant samples — 4 goals across 2 priority tiers, realistic step durations.
→ Action: Updated artifact, verified all field names match the user's types. ✅
→ Tools: visualize:show_widget

---

### Prompt 6: Auditable ledger preview

**Inputs**: text only

> can we add a footer strip showing the last 5 ledger entries? append-only audit log style. timestamp + actor + event type + brief detail

→ Response: Added footer strip with monospace timestamps and event-type color tags.
→ Action: Updated artifact, kept it to 5 visible entries with a "view all" affordance (non-functional in mock). ✅
→ Tools: visualize:show_widget

---

### Prompt 7: Performance check

**Inputs**: text only

> with 50 steps and 10 workers does this still feel snappy? im worried about the pulse animation cost

→ Response: Bumped mock data to 50 steps / 10 workers, animation cost is fine — using transform/opacity only.
→ Action: Tested in artifact, no jank. Recommended virtualizing the step list above ~200 steps. ⚠️
→ Tools: visualize:show_widget

---

### Prompt 8: Color palette concern

**Inputs**: text only

> the priority tier colors are too close to the worker status colors, its visually noisy. can we move tiers to a different channel — maybe left-edge accent bars instead of background fills?

→ Response: Agreed, two competing color signals was the issue. Moved tier to left-edge accent bars (3px), background goes neutral.
→ Action: Updated artifact, much calmer. ✅
→ Tools: visualize:show_widget

---

### Prompt 9: Handoff for next session

**Inputs**: text only

> ok this is solid for tonight. before we wrap, can you list what's still mock and what would need real wiring for v0.1 ship

→ Response: Listed the four real-wiring items: poll endpoint, contract fetch endpoint, ledger stream, theme persistence.
→ Action: Wrote a short follow-up checklist in chat (not as an artifact). 🚧
→ Tools: none

---

**Session summary**: 9 prompts. Built dashboard from whiteboard sketch through 6 iterations to a clean v0.1-ready mockup. Real wiring TODO captured.

<!--
  Trigger prompt ("/log") not logged.
-->
```

---

## What these examples illustrate

- **Filename slugs are specific.** `pkce-vs-auth-code-flow-comparison` not `oauth-question`. `cea-priority-queue-dashboard-build` not `dashboard`. Specificity is what makes timeline sorting useful.
- **Prompt titles describe the move, not the content.** "Worker status colors", "Contract panel", "Performance check" — each one captures *what shifted in the user's thinking*, which is the navigational value.
- **Inputs line is information-dense.** "text + 1 image (whiteboard photo of queue layout sketch)" tells you a lot more than "text + 1 image".
- **Verbatim prompts preserve voice.** "kinda meh", "ok this is solid for tonight", "im worried about the pulse animation cost" — that's how the user actually talks. Don't sanitize.
- **Closing summary is optional and minimal.** Example 1 has none. Example 2 has one short line. Neither has a bullet list.
- **The trigger prompt is excluded** with a small HTML comment at the bottom for clarity.
