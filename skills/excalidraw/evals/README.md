# Excalidraw skill evals

Formal eval harness in the [skill-creator schema](https://github.com/anthropic-experimental/claude-skills/blob/main/skill-creator/references/schemas.md). Derived from three rounds of informal eval (2026-04-19) during skill development.

## Files

| Path | Purpose |
|------|---------|
| `evals.json` | The eval spec — 6 diagrams with programmatic `expectations[]` per skill-creator schema. |
| `files/*-prompt.md` | Input prompts passed to the executor (one per eval). |
| `grade_excalidraw.py` | Programmatic grader. Reads an `.excalidraw`, checks assertions, writes `grading.json`. |

Results go to the sibling workspace at `../excalidraw-workspace/iteration-<N>/`.

## Version control

The skill-creator workflow has no explicit commit/gitignore guidance — here's the split used for this skill:

| Path | Policy | Why |
|------|--------|-----|
| `evals/evals.json` | **Committed** | Source of truth for what "good" means. Small, reviewable. |
| `evals/grade_excalidraw.py` | **Committed** | Reproducibility — without it, `grading.json` files are uninterpretable. |
| `evals/files/*-prompt.md` | **Committed** | Input snapshots used by the executor. |
| `evals/README.md` | **Committed** | This file. |
| `evals/benchmarks/iteration-N.json` | **Committed** | Aggregate only, ~10KB per iteration. Historical record of skill trajectory (R1 88% → R2 92% → R3 94% is a git-log question). |
| `../excalidraw-workspace/iteration-N/<eval>/grading.json` | **Gitignored** | Pure function of (evals.json + raw output). Noisy diffs on re-runs. Regenerable. |
| `../excalidraw-workspace/iteration-N/<eval>/with_skill/outputs/*.excalidraw` | **Gitignored** | Bulky; your existing `local-only/` holds raw outputs outside the skill anyway. |
| `../excalidraw-workspace/` (whole tree) | **Gitignored** via `*-workspace/` pattern | skill-creator's own viewer skips directories named `skill`/`inputs`/`.git` — workspaces are expected to be run-locally. |

The `.gitignore` entry: `skills/*-workspace/` (repo root `.gitignore`).

## Quickstart

Grade one file:

```bash
cd evals
python3 grade_excalidraw.py authoring-patterns /path/to/authoring-patterns.excalidraw
# or by id
python3 grade_excalidraw.py 1 /path/to/authoring-patterns.excalidraw
```

Outputs `grading.json` alongside the `.excalidraw`, listing each expectation's pass/fail/evidence in the skill-creator-compatible format (`expectations[].text/passed/evidence` + `summary`).

Full benchmark across all 6 evals follows the skill-creator workflow:

```bash
# (1) Spawn executor runs (with-skill) for each eval, saving outputs to
#     ../excalidraw-workspace/iteration-N/<eval_name>/with_skill/outputs/<eval_name>.excalidraw
# (2) For each run, grade and save grading.json:
for name in authoring-patterns agentic-ai-auth multi-frame-process agent-sdk-and-harness prompts-to-harness summit-2026-v2-simple; do
  python3 grade_excalidraw.py "$name" \
    "../excalidraw-workspace/iteration-N/$name/with_skill/outputs/$name.excalidraw" \
    --output-dir "../excalidraw-workspace/iteration-N/$name"
done
# (3) Aggregate into benchmark.json:
python -m scripts.aggregate_benchmark \
  ../excalidraw-workspace/iteration-N --skill-name excalidraw
# (4) Open the viewer:
python ~/.claude/skills/skill-creator/eval-viewer/generate_review.py \
  ../excalidraw-workspace/iteration-N --skill-name excalidraw \
  --benchmark ../excalidraw-workspace/iteration-N/benchmark.json
```

For a one-file scripted backfill across all existing rounds, see `../excalidraw-workspace/backfill.py`.

## Expectation design

The assertions are derived from the **failure modes we observed in rounds 1–3** (documented in the repo's `local/ai-docs/excalidraw/` folder, outside this skill). Each maps directly to a real bug class:

| Assertion theme | Origin | Catches |
|-----------------|--------|---------|
| `elbowed: true` on all arrows | R1 bug: some arrows rendered as straight/curved | Arrows Claude forgot to mark elbowed |
| `roughness: 1` on all elements | Brand consistency | Accidental `roughness: 0` crispness drift |
| Arrow `x,y = src.x + fixedPoint[0]*src.width` (±2px) | R1 bug: invisible arrows due to wrong anchor | The load-bearing rule; this single assertion caught the highest-frequency R1 failure |
| Reciprocal `boundElements` / `containerId` | R1 bug: unclickable shapes, lost labels | Shape→text references not both sides |
| No `diamond` type | Excalidraw bug: diamond arrow bindings broken | Accidental diamond choice |
| `roundness: {type: 3}` on content rects | R1 style: sharp corners | Missing rounded-corner brand detail |
| `fontFamily: 5` | Brand (Nunito) | Font drift (e.g. Cole's `fontFamily: 3` monospace) |
| `backgroundColor: "transparent"` | Brand (no fills) | Accidental colored fills |
| `(xN)` = exactly one text element | R1 bug: "Deterministic Logic (x4)" expanded to 4 boxes | `(xN)` multiplicity rule |
| Per-frame mini-legend (swatch count by frameId) | R2 rule | Missing per-frame legends |
| Free-floating text with 3+ lines (multi-line callouts) | R1/R2: Requirements / Outcomes as boxes | Callouts wrongly containerized |
| `mode: "orbit"` on convergence target | R2 hub/convergence pattern | Missing orbit on hub and 6-source convergence |
| Hub rectangle 280–370 × 130–210, `frameId: null` | R3 hub sizing rule | Hub same size as content boxes |
| Dashed retry arrow (`strokeStyle: "dashed"`) | R1 prompt convention | Retry loop rendered solid |
| Single-color palette exhaustive check | Brand palette whitelist | Off-palette colors |

Each assertion is designed to **fail when the skill genuinely misses the rule** — not just when the filename is wrong. The grader's evidence strings quote the exact element id or field value that failed, so regressions are diagnosable without re-opening the diagram.

## Real numbers (backfilled 2026-04-19)

Three iterations graded with this harness (6 evals × 12–16 assertions each):

| Iteration | authoring | agentic-ai-auth | multi-frame | agent-sdk | prompts-to-harness | summit | Mean |
|-----------|-----------|-----------------|-------------|-----------|--------------------|--------|------|
| iteration-1 (R1 baseline) | 88% | 79% | 100% | 85% | 100% | 77% | **88%** |
| iteration-2 (R2 updates) | 100% | 86% | 92% | 85% | 100% | 92% | **92%** |
| iteration-3 (R3 + no-helper rule) | 100% | 86% | 92% | *N/A* | 100% | *N/A* | **94%** excluding rate-limited, 63% counting them as 0% |

iteration-3's agent-sdk and summit were rate-limited before producing output; they count as 0% in the raw mean.

### Assertions that caught real regressions (iteration-1 → iteration-2)

- `authoring-patterns`: `roundness: {type: 3}` on all content rects went from failing (R1 had sharp corners) to passing. This is what made the R2 render "close to perfect."
- `summit-2026-v2-simple`: `(xN) = exactly one text element` went from 2 failing (Det + Agent x4 each expanded in R1) to passing in R2. Direct hit from round-2's (xN) rule.

### Assertions that hold steady

- `elbowed: true`, `roughness: 1`, `no diamonds`, `transparent background`, `fontFamily: 5` — these all pass 100% across all iterations. The skill never drifts on baseline brand rules.

### Known limitations

1. **Semantic-color assertions are shallow.** "Action boxes have `#1e1e1e`" is approximate (there's no way to robustly identify an "action box" without looking at layout context). Marked as MANUAL passes in the grader.
2. **No cross-run variance.** Each iteration is graded once. For proper ±stddev, re-run each eval N≥3 times and aggregate. The skill-creator `aggregate_benchmark.py` handles this when present.
3. **PNG render is a smoke test only.** It checks that the file renders but doesn't compare visually to canonical. Human review through `generate_review.py` covers visual fidelity.
4. **No baseline runs.** We never grade "without_skill" (Claude writing Excalidraw with no reference). The iteration-N benchmarks show skill absolute performance, not the delta. If you want a delta, re-run with a `without_skill` configuration per skill-creator workflow Step 1.

## How to extend

**Add a new eval**: append to `evals.json` with new id, prompt, expected_output, files, expectations. Copy the prompt into `evals/files/`. The grader auto-discovers it by id or eval_name.

**Add a new assertion pattern**: edit `grade_excalidraw.py` — the `check_assertion` function is a dispatcher; add a new `if ... in t:` branch. Use data already loaded into `elements`, `arrows`, `frames`, etc. For assertions that can't be programmatic, write a natural-language assertion and the grader returns `MANUAL` with a pass — you then grade manually via the skill-creator viewer.

**Change the grading output format**: the grader writes skill-creator-compatible `grading.json`. If your workflow uses different field names, wrap it — don't edit. The viewer (`generate_review.py`) depends on `text`/`passed`/`evidence` exactly.
