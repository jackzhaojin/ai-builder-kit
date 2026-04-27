# Sample Input — What a Good Source Document Looks Like

This is a **reference input** for the drawio skill. It shows the shape of a source document that lets the skill produce a high-quality diagram on the first pass without an interview round.

When a user hands you a markdown like this, you should be able to:
- Pick the visual pattern in Step 0 without asking.
- Place every component without inferring its role.
- Color and group every component without guessing.
- Pre-empt the dash-overload, missing-cylinder, and prompt-vs-source mistakes documented in `SKILL.md`.

If the user's actual input is missing any of the sections below, that section becomes an **interview question** at Step 0 (see `SKILL.md` → *Required Information*).

---

## Executive Summary

> One paragraph: what is this system, who uses it, what does the diagram need to argue?

**Example.** "Order-fulfillment platform that ingests customer orders from a public storefront, runs them through deterministic validation and an AI-driven fraud check, then routes valid orders to a warehouse-management system. The diagram should make clear which steps are deterministic vs agentic and where the data stores live."

---

## Diagram Type

- [x] Architecture (components, services, infrastructure)
- [ ] Process (workflow, timeline, steps)

## Complexity

- [ ] Simple (5–10 boxes)
- [x] Medium (15–25 boxes)
- [ ] Complex (30+ boxes)

---

## Subsystems / Frames

Each subsystem becomes a swimlane frame.

| Frame | Role | Talks to |
|-------|------|----------|
| `storefront` | Public-facing order entry (web + mobile clients) | `order-core` |
| `order-core` | Validation, fraud check, persistence, dispatch | `storefront`, `warehouse` |
| `warehouse` | Third-party WMS — receives validated orders, returns fulfillment status | `order-core` |

---

## Components (per Subsystem)

### `storefront`

| Component | Role | Owner | Color |
|-----------|------|-------|-------|
| Web App | Browser client (React) | Internal | User/Default |
| Mobile App | iOS/Android client | Internal | User/Default |
| API Gateway | Auth, rate limiting, request routing | Internal | Deterministic |

### `order-core`

| Component | Role | Owner | Color |
|-----------|------|-------|-------|
| Order Validator | Schema + business-rule validation | Internal | Deterministic |
| Fraud Check | LLM-driven anomaly detection | Internal | Agentic |
| Order Dispatcher | Routes valid orders to WMS | Internal | Deterministic |
| Orders DB | Persistent order records | Internal | Deterministic |
| Audit Log | Append-only log of all decisions | Internal | Deterministic |

### `warehouse`

| Component | Role | Owner | Color |
|-----------|------|-------|-------|
| WMS API | Third-party warehouse-management endpoint | External (vendor: `wms.example.com`) | User/Default |

---

## Data Stores

List data stores **separately** from services. Each gets its own cylinder, even if one service owns multiple.

| Store | Owner | Type | Notes |
|-------|-------|------|-------|
| Orders DB | `order-core` / Order Validator | Postgres | Persistent order records, indexed by order ID |
| Audit Log | `order-core` / Order Validator | Append-only log | Every validation + fraud decision, retained 90 days |

> If `order-core` had been described as "Order Validator owns persistence (Postgres + audit log)" in prose, that would compress to one rectangle and lose the two-store distinction. Listing them in a table forces the cylinder treatment.

---

## Cross-Cutting Concerns

Concerns that apply across multiple frames. Decide upfront where they render.

| Concern | Placement |
|---------|-----------|
| Auth (OAuth) | Inside `storefront` (API Gateway) — not a separate frame |
| Telemetry / metrics | Omitted from diagram (mention in caption) |
| HITL fraud review | Dedicated row inside `order-core` for the human reviewer |

Possible placements: **global bar above all frames** / **own swimlane** / **inside an existing frame** / **omit from diagram**. Pick one per concern.

---

## Edges

List the edges that *matter* — not every wire, just the ones the diagram is making an argument about.

| From | To | Kind | Notes |
|------|----|------|-------|
| Web App | API Gateway | Forward (request) | Solid black |
| Mobile App | API Gateway | Forward (request) | Solid black |
| API Gateway | Order Validator | Forward (request) | Solid blue (deterministic) |
| Order Validator | Fraud Check | Forward (request) | Solid red (agentic) |
| Fraud Check | Order Validator | **Return** (response) | **Dashed** red |
| Order Validator | Orders DB | Write | Solid blue |
| Order Validator | Audit Log | Write | Solid blue |
| Order Validator | Order Dispatcher | Forward | Solid blue |
| Order Dispatcher | WMS API | Forward (cross-frame) | Solid black |
| WMS API | Order Dispatcher | **Return** (status) | **Dashed** black |

> **Note on dashed.** Only the two return edges (Fraud Check → Validator, WMS API → Dispatcher) are dashed. Forwards are solid. This is the only meaning dashed carries — see `diagram-style.md` §6.

---

## Style Hints

| Decision | Choice |
|----------|--------|
| Color axis | **Determinism** (skill default — blue/red/orange/black) |
| Flow direction | Left-to-right at the frame level (storefront → order-core → warehouse), top-to-bottom inside each frame |
| Exception highlighting | None — no exception flow in this diagram |
| Legend | Top-left (multi-frame diagram) |

---

## Prompt vs Source — Known Caveats

Things the human asked for that **disagree with this source doc**, so the model must reconcile at Step 0:

> *(none in this example — but if the prompt said "show WMS as part of order-core," that would contradict the source's "External vendor, separate frame" and require a clarifying question)*

When this section is non-empty, the skill must flag each item and ask before generating.

---

## What's NOT Here (and Why)

The skill should *not* invent these:
- Specific RPS / latency numbers (not provided, not relevant to architecture diagram)
- Internal data schemas (out of scope)
- Deployment topology (separate diagram)
- Telemetry pipeline (explicitly omitted under Cross-Cutting Concerns)

---

## Output Mapping

The resulting diagram for this input should:
- Have **3 swimlane frames** (`storefront`, `order-core`, `warehouse`) arranged left-to-right.
- Show **2 cylinders** inside `order-core` (Orders DB, Audit Log) connected to the Order Validator box.
- Use **3 colors**: blue (deterministic), red (agentic), black (default).
- Have **2 dashed edges** total — both are return paths (Fraud Check → Validator, WMS API → Dispatcher). Every other edge is solid.
- Show the WMS API as a single box inside the `warehouse` frame, labelled with the vendor identifier.
- Place the legend top-left at the canvas level (multi-frame diagram).

Compare against `multi-container-3tier.{drawio,png}` for the closest existing rendered example of a 3-frame layout with cross-frame edges.
