---
name: competing-pr-triage
description: Compare two pull requests or two branches that were produced by different agents attempting the same goal, and recommend which one to adopt. Use when the user asks to "compare PR X and PR Y", "which branch is better", "two agents gave me different PRs for the same task", "triage competing PRs", or any situation where multiple worktrees/branches solved (or attempted) the same goal in parallel and a decision is needed on which to merge or continue from. Produces a functional-requirements table with per-requirement verdicts, a file-level scope audit (extras check), a branch recommendation, and a concrete follow-up plan for what the agent should do after switching to the chosen branch.
---

# Competing PR Triage

## When this fires

The user has **two (or more) PRs/branches that targeted the same goal** and wants a decision on which to adopt. Typical phrasings:

- "Look at PR 17 and 18, same task, which one makes sense?"
- "Two agents came back with different PRs, triage them"
- "Which worktree should I keep?"
- "Compare branch A vs branch B"

This is specifically for the **parallel-agent / multi-worktree workflow**: the user spawned multiple agents on the same goal and needs to pick a winner.

## Required inputs

Before analysis, the skill needs three things. Ask only for what's missing — infer the rest from context.

1. **Two PR numbers OR two branch names.** `gh pr view <N>` works for PRs; `git diff main..<branch>` for local branches.
2. **The goal / task the agents were trying to solve.** Look in this order:
   - A goal doc linked or referenced in either PR body (e.g., `ai-docs/…/goal-X.Y.Z.md`)
   - The PR description itself if it restates the requirements
   - A `workspace/` bundle `PROMPT.md`
   - If none of the above exist, **ask the user** where the original ask lives — do not invent requirements.
3. **(Optional) User priorities** — e.g., "I care more about scope discipline than functional coverage." Default: weight functional coverage and scope discipline equally.

**Do not proceed to analysis without the goal doc.** Every row in the output table must trace back to a requirement in the goal. If there is no authoritative requirements list, the "Maps to goal?" column is meaningless.

## Workflow

### Phase 1 — Gather

Run these in parallel whenever possible:

```bash
gh pr view <N1>                                    # title, body, labels, state
gh pr view <N2>
gh pr diff <N1>                                    # full diff
gh pr diff <N2>
gh pr view <N1> --json files -q '.files[].path'    # file list only
gh pr view <N2> --json files -q '.files[].path'
```

For local branches, substitute `git diff main..<branch>` and `git diff --name-only main..<branch>`.

Then **read the goal doc** referenced by either PR. Extract:

- The numbered requirements list (R1, R2, … or equivalent)
- The success criteria / definition of done
- Any "options" the spec offered (Option A/B/C) — a PR that chose a different option than spec should be flagged, not failed

### Phase 2 — Map requirements to PR changes

For each requirement in the goal doc, classify each PR as:

- **Implemented** — real code change addresses the requirement
- **Not addressed** — silently skipped
- **Partial** — addressed but gap remains
- **Reframed** — the PR edited the requirement text itself instead of implementing it (critical failure mode; flag loudly)

Trace each code change back to a requirement. A change that doesn't map to any requirement is an **extra** (see Phase 3).

### Phase 3 — File-level scope audit (the "extras" check)

For each PR, build a table: `file | change summary | maps to requirement?`. Every file must map 1:1 to a goal requirement, a success criterion, or honest progress tracking (e.g., flipping checkboxes in the goal doc). Anything else is scope creep:

- Drive-by refactors unrelated to the goal
- Dependency bumps not required by the task
- README / CHANGELOG additions the user didn't ask for
- New abstractions introduced "while we're here"
- Rewriting the spec instead of implementing it (critical failure)

**Score:** `extras_count = files_not_mapping_to_requirement`. Lower is better. A PR with 0 extras is perfectly scoped.

### Phase 4 — Non-functional aspects

Consider these for each PR (skip rows with no meaningful difference):

- Type safety / typecheck passes
- Backward compatibility (did it break existing callers?)
- Test / build evidence in the PR body
- Blast radius & safety (unscoped `pkill`, destructive migrations, secrets handling)
- Observability / logging additions that pay for themselves
- Robustness of detection heuristics (keyword match vs tag-based, magic strings)
- Scope discipline (same signal as extras, captured as a row for visibility)
- Honest progress tracking (flipped only the checkboxes it actually completed)

### Phase 5 — Render the output

The output has **four sections, in this order**. Do not skip or reorder.

#### 1. Functional requirements table

| Requirement | PR #A | PR #B | Maps to goal? | Verdict |

- One row per requirement from the goal doc, plus one row for each distinct success criterion
- PR columns contain a concrete implementation summary ("Implemented — `file.ts` adds X") or "Not addressed"
- **Maps to goal?** column explicitly cites the requirement ID (R1, R2, …). For reframed rows, mark `⚠️ Rn — asked but PR edited spec instead of solving`
- Verdict: `**PR #A**`, `**PR #B**`, `**Neither**`, or `**Tie**` — bolded

#### 2. File-level scope audit (one sub-table per PR)

| File | Change | Maps to requirement? |

- Every file the PR touched
- Right column uses ✅ for needed changes with the requirement ID, ⚠️ for ambiguous, ❌ for extras
- Conclude each sub-table with `**Extras in PR #X: N files.**`

#### 3. Non-functional aspects table

| Aspect | PR #A | PR #B | Verdict |

Include only rows with meaningful differences.

#### 4. Verdict and follow-up plan

A 4-part closing:

1. **Recommendation** — one sentence: which PR to adopt and why (functional coverage + extras count).
2. **Switch-to-branch instructions** — the exact next moves after `gh pr checkout <N>` or `git switch <branch>`. Must be a concrete, prioritized list:
   - Fixes needed before merge (with file:line references where known)
   - Any unaddressed requirements still open
   - Success criteria still unverified (e.g., E2E not run)
   - Whether to close the losing PR or salvage parts of it
   - **Merge mode**: default to `gh pr merge <N> --merge` (creates a merge commit, preserves individual commits including any review-driven pre-merge fixes). **Do NOT squash by default.** Only suggest `--squash` when the branch is full of noisy fixup/WIP commits that genuinely aren't worth preserving AND there were no meaningful post-triage review fixes. When the triage process itself added pre-merge fixes, squashing erases the separation between "what the agent did" and "what the review caught" — that distinction is exactly what this skill exists to surface, so preserve it in history.
3. **What the losing PR contributes** — if parts are worth cherry-picking, say so. If it's pure noise, say "close without merging."
4. **Suggested next actions for the user** — a short numbered menu the user can pick from in their next reply. The skill itself does not execute these; it just makes it cheap for the user to say "do option 2" and have the agent act in the same context. Keep to 3–5 options, each a single imperative line. Example:

   > **Want me to take any of these next?**
   > 1. Checkout PR #17 and apply the two pre-merge fixes (scope `pkill`, swap heuristic for tag-based detection)
   > 2. Checkout PR #17 as-is and run `npm run typecheck && npm run build` to confirm it's clean locally
   > 3. Close PR #18 with a comment linking to this analysis
   > 4. Draft a follow-up goal bundle for R5 (POC reference handling) and the E2E success criterion
   > 5. Do nothing — just wanted the assessment

   Always include a "do nothing" option so the user doesn't feel pushed into action. Tailor options 1–4 to what the analysis actually surfaced — don't invent generic ones.

## Scoring guidance (how to actually pick a winner)

Two axes matter most:

1. **Functional coverage** — `count(requirements_implemented) / count(requirements_in_goal)`
2. **Scope discipline** — `1 - (extras_files / total_files_touched)`

Tiebreakers, in order: test evidence > blast radius > robustness of implementation choices > diff size (smaller wins when coverage is equal).

## Merge mode policy

**Default: `--merge` (standard merge commit).** Preserves all feature-branch commits plus a merge commit tying them together. Keeps full traceability — especially important when the triage review added pre-merge fix commits, because those fixes should remain distinct from the original agent's work in history.

**Use `--squash` only when all of these are true:**
- The branch has messy fixup/WIP commits (typos, "oops", revert-then-redo sequences)
- None of those commits carry meaningful review context worth preserving
- The PR title captures the whole unit of work cleanly in one line

**Use `--rebase` only when** the branch is already well-curated (every commit meaningful) AND the project prefers a linear history.

**Anti-pattern:** squashing a PR that just received review-driven pre-merge fixes. That erases the distinction between "what the original agent produced" and "what the review caught," which is exactly the signal this skill exists to preserve. Future retrospectives on agent performance depend on that distinction being visible in history.

**Critical failure modes that auto-disqualify a PR regardless of other scores:**

- **Spec rewriting**: the PR edits requirement text instead of implementing it. This is worse than doing nothing because it makes the goal ambiguous going forward.
- **Silently breaks existing behavior**: removes a feature not mentioned in the goal, or changes a public API without migration.
- **Dishonest progress tracking**: flips success-criteria checkboxes it didn't actually implement.

Call these out explicitly in the verdict — do not bury them in the table.

## Tone & format

- **Be direct.** The user wants a decision, not hedging. "Merge PR #17, close PR #18" is the right voice.
- **Cite evidence.** Every verdict references specific files, specific requirement IDs, or specific lines. No vibes-based judgments.
- **Flag implementation nits inside the winning PR** separately from the win/loss decision. A PR can win on coverage and still need two fixes before merge — say so.
- **Never exceed what was asked.** Don't propose architecture changes beyond the follow-up plan. Don't recommend writing tests the goal didn't require.

## Anti-patterns to avoid

- **Do not analyze without the goal doc.** If you can't find it, ask the user.
- **Do not treat "more lines changed" as "more work done."** A 9-line PR that solves the task beats a 400-line PR that solves half of it.
- **Do not reward size.** In the canonical PR #17 vs #18 case, the 9-line PR was worse because it didn't implement anything.
- **Do not conflate "I agree with this design choice" with "this meets the requirement."** Keep design preferences in the "implementation nits" section.
- **Do not skip the file-level scope audit.** It's the fastest way to catch reframed-spec PRs and drive-by refactors.

## Worked example

See `references/example-output.md` for a full worked example based on PR #17 vs PR #18 (goal-2.1.5 Worker Reliability). Read it when you need a concrete template for the four output sections.
