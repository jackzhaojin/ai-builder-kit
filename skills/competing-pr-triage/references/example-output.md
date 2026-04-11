# Worked example: PR #17 vs PR #18 (goal-2.1.5)

This is a canonical example of the four output sections. Use it as a template.

**Goal source:** `ai-docs/v2/2026-04-01-v2.1/goal-2.1.5.md` — Worker Reliability & Verification Hardening. Six requirements (R1–R6) plus one E2E success criterion.

**Context:** User spawned two agents (Codex, Claude) on the same task. Both came back with PRs. Codex produced a 104/−27 implementation across 7 files; Claude produced a 9/−9 doc-only edit.

---

## 1. Functional requirements table

| Requirement | PR #17 (Codex) | PR #18 (Claude) | Maps to goal? | Verdict |
|---|---|---|---|---|
| **R1: Hard-fail `node_build`** | Implemented — `validateWorkDetailed` + `isLikelyWebProject` heuristic, `node_build` added to blocking verifiers | Not addressed | ✅ R1 | **PR #17** — heuristic is fragile, prefer tag/frontmatter |
| **R2: Dynamic port detection** | Implemented — 3-tier fallback in `web-testing/SKILL.md` | Not addressed | ✅ R2 | **PR #17** |
| **R3: Orphan dev-server cleanup** | Implemented — `pkill` in `setupAgentOutputsRoot()` | Not addressed | ✅ R3 | **PR #17** — needs scoping |
| **R4: Build error in retry context** | Implemented — `retry.lastError` prefixed with `buildError` | Not addressed | ✅ R4 | **PR #17** |
| **R5: Update/prune POC refs** | Not touched | Rewrites R5's framing, no implementation | ⚠️ R5 — asked but PR edited spec instead of solving | **Neither** |
| **R6: Per-step `build_health`** | Implemented — `WorkStep` fields + persistence + loop wiring | Not addressed | ✅ R6 | **PR #17** |
| **E2E: 32-step web app renders** | Not demonstrated | Not addressed | ✅ Success criterion | **Neither** |

## 2. File-level scope audit

### PR #17

| File | Change | Maps to requirement? |
|---|---|---|
| `ai-docs/v2/2026-04-01-v2.1/goal-2.1.5.md` | Flips 5 checkboxes, status → In Progress | ✅ Progress tracking for R1/R2/R3/R4/R6 |
| `claude-files-to-output/skills/web-testing/SKILL.md` | 3-tier port detection, `${PORT:-3000}` fallback | ✅ R2 |
| `src/agentic/execution/worker-spawner.ts` | `pkill` stale dev servers before spawn | ✅ R3 |
| `src/core/types.ts` | Adds `build_health` + `build_error` to `WorkStep` | ✅ R6 |
| `src/deterministic/steps-json-handler.ts` | `updateStepStatus` extras widened | ✅ R6 |
| `src/deterministic/validation-handler.ts` | `validateWorkDetailed` + `ValidationOutcome` | ✅ R1 + R4 |
| `src/core/executive-loop.ts` | Calls detailed validator, writes `build_health`, prefixes retry error | ✅ R1 + R4 + R6 wiring |

**Extras in PR #17: 0 files.**

### PR #18

| File | Change | Maps to requirement? |
|---|---|---|
| `ai-docs/v2/2026-04-01-v2.1/goal-2.1.5.md` | Renames R5 title, rewrites problem statement, replaces options list | ❌ Rewrites spec instead of implementing R5 |

**Extras in PR #18: 1 file (100% of the PR).**

## 3. Non-functional aspects

| Aspect | PR #17 | PR #18 | Verdict |
|---|---|---|---|
| Code changes | 104 / −27 across 6 code files + 1 doc | 9 / −9 in 1 doc file | **PR #17** |
| Type safety | Clean extension of `WorkStep`; `ValidationOutcome` exported | N/A | **PR #17** |
| Back-compat | `validateWork` kept as wrapper over `validateWorkDetailed` | N/A | **PR #17** |
| Build evidence | typecheck + build pass per PR body | None | **PR #17** |
| Blast radius | `pkill` unscoped — could kill user's unrelated `next dev` / `vite` | None | **PR #18** safer only by doing nothing |
| Heuristic robustness | R1 keyword match on title/description; misses goals without magic words | N/A | PR #17 nit — fix before merge |
| Scope discipline | 7/7 files map to requirements | 0/1 files implement anything | **PR #17** |
| Honest progress tracking | Flips 5/7 checkboxes (correctly leaves R5 + E2E open) | Flips nothing | **PR #17** |

## 4. Verdict and follow-up plan

**Recommendation:** Merge PR #17, close PR #18. PR #17 covers 5/6 requirements with zero scope extras; PR #18 covers 0/6 and its only change is a spec rewrite — a critical failure mode that makes R5 ambiguous going forward.

**Switch-to-branch instructions** (after `gh pr checkout 17`):

1. **Before merge — two fixes required:**
   - `src/deterministic/validation-handler.ts:isLikelyWebProject` — replace keyword match with tag-based detection. Use `item.tags?.includes('web' | 'nextjs' | 'react')` or add a `hard_verifiers` field to PROMPT.md frontmatter per R1 Option B.
   - `src/agentic/execution/worker-spawner.ts` — scope the `pkill` cleanup. Currently it kills any `next dev`/`vite`/`react-scripts start` process on the machine. Narrow it to processes whose CWD is under `AGENT_OUTPUTS_BASE`, or track child PIDs from prior spawns in state.
2. **Still open after merge:**
   - **R5** (POC references) — decide whether to vendor-gate POC injection in `prompt-builder.ts` or remove `references/poc/claude/*` from `worker-base` entirely. The reframe in PR #18 is reasonable input for this discussion but should land as a follow-up PR, not a spec edit.
   - **E2E success criterion** — run a 32-step web goal end-to-end with the new hard-fail gate active and verify the app renders at the end.
3. **Close PR #18** without merging. Its framing change is fine as a comment on the goal doc; it should not land as "progress on 2.1.5."

**What the losing PR contributes:** The R5 reframing in PR #18 (shift from "prune Claude-only POCs" to "inject vendor-specific POCs") is a reasonable design direction and can be cherry-picked as a comment or captured as an issue for the R5 follow-up. Nothing else from PR #18 is worth keeping.

**Want me to take any of these next?**

1. Checkout PR #17, apply the two pre-merge fixes (scope `pkill` to `AGENT_OUTPUTS_BASE`, unify web detection via `WEB_KEYWORDS`), then `gh pr merge 17 --merge` (preserves individual commits — do not squash, the review-driven fixes are worth keeping distinct in history)
2. Checkout PR #17 as-is and run `npm run typecheck && npm run build` to confirm it's clean locally before you decide
3. Close PR #18 with a comment linking to this analysis and capturing the R5 reframing as a follow-up issue
4. Draft a follow-up goal bundle for R5 (POC reference handling) and the E2E 32-step success criterion
5. Do nothing — just wanted the assessment
