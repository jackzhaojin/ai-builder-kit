# Spirit of the AI Knowledge Harvester

> *"The idea here is that most likely we'll have an AI driven process where a skill writes to this.
> So it's like a secret repository where I keep all my AI stuff."*
> — Jack, the conversation that created this skill

---

## Why This Exists

This skill was born out of a recognition that AI-assisted development has outgrown ad-hoc prompting.
After months of building with Claude Code, Codex CLI, and continuous agents, a pattern emerged:
AI documents — specs, prompt logs, gap analyses, kickoff prompts — were scattered across every
repository, checked into git alongside code, sometimes gitignored, sometimes not, and increasingly
unmanageable as the pace of building accelerated.

The problem wasn't just organization. It was *recoverability*. If an agent needed to understand how
a past project was structured, or what patterns had worked, it had no way to find that across
repositories. And if a human wanted to understand their own AI working patterns — the prompts that
led to breakthroughs, the specs that saved sessions, the decisions made at 10pm — those were buried
in commit histories across a dozen repos.

---

## The Thinking That Shaped This

The conversation that produced this skill explored several storage options:

**Notion** — great human interface, terrible for bidirectional markdown sync. Notion stores a
proprietary block tree, not markdown. Round-tripping is lossy. Agents would need conversion layers.

**Cosmos DB** — attractive for its native JSON document storage and vector search capability.
Appealing for an application layer. But overkill for what was immediately needed, and poor human
browsability without a generated view layer.

**Airtable** — good for structured records, awkward for freeform documents.

**GitHub + Private Repo + Markdown** — won. Here's why it was the right answer:
- Agents already use git. Writing and committing markdown costs essentially zero to implement.
- GitHub renders markdown beautifully. Human browsing is solved for free.
- Private repo gives "hidden by default" with credential-based access.
- No lock-in. Vector search can be bolted on later by indexing the repo.
- Migration from any other system can be automated.
- Obsidian works as a local lens onto a GitHub-backed store — a well-worn pattern.

**On OIDC vs PAT**: GitHub OIDC was considered for cloud agent access, but it's designed for
human login flows. For machine-to-machine access from cloud agents (Claude Code, Codex CLI on
Oracle VM), a fine-grained Personal Access Token scoped to the single private repo is simpler,
rotatable, and correct.

---

## The Taxonomy Decision

Three organizing philosophies were considered:

1. **Chronological first** — matches human memory ("I remember doing this in January") but makes
   topic-based retrieval hard for agents.

2. **Type first** — clean for pattern mining (all prompt logs in one place) but splits related
   project files across the tree.

3. **Project first with type and date within** ⭐ — chosen. Projects are the most durable
   taxonomy. They outlive date schemes and type classifications. Everything about a project lives
   together. Date-prefixed filenames give chronological order within type buckets without a
   separate date folder layer.

**The "folder IS the taxonomy" principle**: No central index file that needs constant maintenance.
The folder structure itself communicates where things live. Each file carries its own YAML
frontmatter for self-documentation and future indexing. When pattern mining is needed, a skill
can regenerate any index from frontmatter.

**Three document types recognized:**
- `specs/` — stable reference documents, written once, consumed by agents at task start
- `prompt-logs/` — session transcripts, append-only, chronological, the future pattern-mining corpus
- `working-docs/` — living documents that evolve (gap analyses, kickoff prompts, operational guides)

**why-private.md at the project root**: Every project explains why it's in the private repo
and not open source. The privacy rationale matters — if it can't be stated, maybe it should
be open sourced.

---

## The Open Source Philosophy

Jack's broader goal is to make as much as possible open source, keeping private only what
genuinely needs to be:

> "I want to kind of clean up all my private repositories and make everything as open source
> as possible and then kind of slowly opening source my capabilities, however keeping what I
> think should be private in a centralized way."

The layered abstraction insight: whatever *generates* the harness is the secret thing.
The harness output can be open. The harness's output's output definitely can be open.
Secrecy requirements decrease as you go deeper into automation.

This skill itself is intentionally public — the *mechanism* for harvesting is shareable.
The *repository it writes to* is private. The skill is the recipe; the ingredients are yours.

---

## What Comes Next

This skill handles **Requirement 1**: current project context — getting AI docs organized
and findable so a working agent can pull relevant context at task start.

**Requirement 2** — pattern mining across prompt logs to build new harnesses and skills —
is deliberately deferred. The infrastructure (organized repo, consistent frontmatter, typed
document buckets) built here creates the foundation. When enough prompt logs accumulate,
a future skill will index them, find patterns, and generate new capabilities from them.

The right time to build the vector search layer is when you have enough documents that
search actually matters. Don't build it until then.

---

## Lineage

This skill was designed in a conversation on 2026-03-28 drawing on:
- The Continuous Executive Agent V1 Constitution (2026-01-24)
- The V1.2 PRD and its Goal State Machine / Project Memory features
- Real AI docs from the ciam-demo project (prompt logs, specs, gap analyses)
- The principle that AI systems should build real things and validate through construction

The pattern of "skills become the shared foundation across all execution contexts" from the
V1.2 architecture directly inspired making this a reusable skill rather than a one-off script.

---

*This skill is the beginning of the agent knowing itself.*
