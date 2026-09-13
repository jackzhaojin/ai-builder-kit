# Visual Patterns

Shapes that diagrams can take. A diagram should **argue a point**, not just display components. Picking a pattern that matches the argument is often more important than the specific components.

This file is the pattern library. Use it during Step 0 (plan sections first) to pick an overall shape before placing any element.

## Table of contents
- [Assembly line](#assembly-line)
- [Timeline](#timeline)
- [Fan-out (one-into-many)](#fan-out-one-into-many)
- [Convergence (many-into-one)](#convergence-many-into-one)
- [Hub with spokes](#hub-with-spokes)
- [Tree / hierarchy](#tree--hierarchy)
- [Side-by-side comparison](#side-by-side-comparison)
- [Gap / break](#gap--break)
- [Loop / cycle](#loop--cycle)
- [Cloud / system boundary](#cloud--system-boundary)

## Assembly line

Linear transformation: input → step 1 → step 2 → … → output. Each stage changes the thing.

Best for: data pipelines, build steps, render pipelines, content production. Left-to-right usually reads best.

```
[ Input ] → [ Step 1 ] → [ Step 2 ] → [ Step 3 ] → [ Output ]
```

- One color per stage type if stages have different semantic categories (e.g. blue for Python, purple for AI).
- Arrows are straight (2-point).
- Resist the urge to annotate each stage with code snippets or captions — per `brand-style.md` § "Whitespace is pretty", a well-named stage doesn't need a description underneath.

Argues: "things happen in this order, and each step does exactly this."

## Timeline

Chronological sequence of events, usually annotated with dates or phase labels. Variation of assembly line but with time as the axis.

```
[2026-01]      [2026-03]      [2026-06]      [2026-09]
   ●──────────────●──────────────●──────────────●
  AI part 1     Inflection    MCP rollout   Agent v2
```

- Dots on a line, with labels.
- Each milestone ellipse or dot is a fixed color; the connecting line is neutral grey.
- Free-floating date labels above; descriptive labels below.

Argues: "these things happened (or will happen) in this order, and here's the spacing."

## Fan-out (one-into-many)

One source, N outputs. See arrows.md § "Fan-out pattern" for JSON recipe.

```
                 ┌──→ [ A ]
[ Source ]──┬────┼──→ [ B ]
            │    └──→ [ C ]
```

Best for: AI outputs (one prompt → 3 artifacts), branching decisions, children in a taxonomy.

Argues: "one thing produces these several things."

## Convergence (many-into-one)

N inputs merge into one. See arrows.md § "Convergence pattern" for JSON recipe.

```
[ A ]──┐
[ B ]──┼──→ [ Target ]
[ C ]──┘
```

Best for: inputs merging into a pipeline, prerequisites funneling into a decision, stakeholder inputs to a final output.

Argues: "these several things together produce this one thing."

## Hub with spokes

One central hub, N surrounding subsystems all talking to it. See section-layout.md § "Worked example: hub with spokes." The hub binding uses `mode: "orbit"` so arrows distribute around edges automatically.

```
        [Frame A]
           │
[Frame D]─[Hub]─[Frame B]
           │
        [Frame C]
```

Best for: event-bus architectures, orchestration coordinators, central document being edited by multiple agents.

Argues: "everything coordinates through this one thing."

**Hub sizing:** 280×140 to 350×200 — deliberately bigger than the default 200×100 content box so it reads as the center. Label `fontSize: 24–28` (bigger than content boxes' 20). Stroke `#1e1e1e`, rounded corners (`roundness: {type: 3}`), same `strokeWidth: 2`. Centered on canvas with 200–400px gap to each surrounding frame.

## Tree / hierarchy

Parent → children → grandchildren. Fan-out applied recursively.

```
              [ Root ]
               /   \
           [A]       [B]
          /  \      /  \
       [A1] [A2] [B1] [B2]
```

Best for: taxonomies, org charts, file trees, decision trees.

Argues: "this thing contains these things, which contain these things."

## Side-by-side comparison

Two independent columns (or sections) shown in parallel for comparison. See section-layout.md § "Worked example: side-by-side architectures."

```
 Column A         │         Column B
 ┌──────┐         │          ┌──────┐
 │      │      divider       │      │
 └──────┘         │          └──────┘
```

Best for: before/after, option A vs option B, two systems evolving in parallel.

Argues: "these two things are worth comparing directly."

## Gap / break

A **deliberate gap** between two regions to signal separation. Often a small icon in the gap (`⟂`, `⚡`, `✂`) or a label like "trust boundary" / "network hop."

```
[ Internal ]───┐     ┊     ┌───[ External ]
                     ┊
                 trust
                boundary
```

Best for: security boundaries, system boundaries, network boundaries, team boundaries.

Argues: "a meaningful gap exists here — these two sides are not the same."

## Loop / cycle

A flow that feeds back into itself. Usually a row left-to-right with a return arrow curving below.

```
[A] → [B] → [C] → [D]
 ▲                 │
 └─────retry───────┘
```

- The return arrow is usually **dashed** (indicates retry / optional path).
- The return arrow color is muted (`#bbb`) or matches the failure semantic (red).

Best for: retry loops, polling, feedback loops, iterative processes.

Argues: "this process can repeat or correct itself."

## Cloud / system boundary

A large dashed rectangle (or cloud shape, but per brand-style.md use a frame) that contains several elements and represents "this whole thing is one system or external service."

Use Excalidraw `frame` with a descriptive name. Don't use dashed rectangles — frames group explicitly and render more cleanly.

Best for: "everything inside this region is AWS," "this entire block is owned by team X," "this whole thing is one docker-compose stack."

Argues: "everything in here belongs together — boundaries matter."

---

## Picking a pattern

Given the argument you want to make:

| Argument | Pattern |
|----------|---------|
| "Things happen in this order." | Assembly line, timeline |
| "One thing produces these." | Fan-out |
| "These produce one thing." | Convergence |
| "Everything coordinates through this." | Hub with spokes |
| "Compare A vs B." | Side-by-side |
| "These two regions are separate." | Gap / break |
| "This process can repeat." | Loop / cycle |
| "This region is one unit." | Cloud / system boundary (frame) |
| "Tree of things." | Tree / hierarchy |

Pick the pattern first, lay out frames second, fill elements third. Not the other way around.
