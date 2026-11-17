# Changelog

What changed in each release of ai-builder-kit, newest first. One version covers the whole repo: it lives in `plugin.json`, `.codex-plugin/plugin.json` and the top of `.claude-plugin/marketplace.json`, and each release is tagged `vX.Y.Z` in git.

Installs do not wait for a release. Skill entries carry no version, so every push to `main` that touches a skill reaches users on their next update (see "Keeping it up to date" in [README.md](README.md)). A release is a checkpoint that says what those pushes added up to.

- **Major**: a skill changes behavior that users have to know about, such as a `!` commit
- **Minor**: a new skill or a new capability in one
- **Patch**: fixes and docs

The guarded hook plugin keeps its own version in `plugins/hlx-admin-api-executor-guarded/.claude-plugin/plugin.json`, because its folder only holds a symlink to the skill.

## 3.0.0 - 2026-11-16

### Breaking

- `jack-git-commit`: commits and pushes finished work to the current branch by default instead of never pushing. A project that should not push has to say so in its own instructions. Public repos get a read of the diff before the push, critical work still stops to ask, and force-push stays off. The skill also stages exact paths instead of `git add -A`, no longer asks to approve each commit, and splits mixed changes into separate commits without asking.

### Fixed

- `hlx-admin-api-executor-guarded` (plugin 1.1.0): the guard hook only caught `-X POST` written with a space. It now treats any explicit write method, request body or upload as a write (`-XPOST`, `--request=DELETE`, `-d`, `--data-binary`), covers the `api.aem.live` host, and still lets GETs through.
- `hlx-admin-api-executor`: sites authored in Document Authoring accept an Adobe IMS token as `Authorization: Bearer`, so the skill uses that instead of a cookie copied from DevTools, and it names the `api.aem.live` org/sites path form.
- `branded-pptx` and `podcast-slides-video`: their Python scripts declare dependencies inline (PEP 723) and run with `uv run`, so nothing has to be installed into the system Python.
- `excalidraw`: eval benchmark evidence paths are relative.

### Changed

- `hlx-admin-api-executor-guarded` (plugin 1.1.1): the plugin's skill is a symlink to `skills/hlx-admin-api-executor` instead of a copy that could drift, and the hook uses exec form. Its version now lives only in its `plugin.json`.

### Repo

- CI runs `scripts/check-repo.mjs`, the Claude Code plugin validator and ShellCheck on every push to `main` and every PR.
- This changelog and the `vX.Y.Z` release tags. `v2.0.0` was tagged after the fact on the commit that introduced it.
- README and CLAUDE.md refreshed, `AGENTS.md` is a symlink to `CLAUDE.md`, and the docs name `plugin.json` as the manifest Codex reads first.

## 2.0.0 - 2026-09-13

First release with a version number, set when the repo became a Codex marketplace as well (`plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`). Added the `excalidraw` and `podcast-slides-video` skills.

Skills: `ai-knowledge-harvester`, `branded-pptx`, `chat-conversation-logger`, `competing-pr-triage`, `conversation-logger`, `drawio`, `excalidraw`, `hlx-admin-api-executor`, `jack-git-commit`, `playwright-demo-video`, `podcast-slides-video`. Plugin: `hlx-admin-api-executor-guarded` 1.0.0.

Before 2.0.0 the repo had no version. Its history goes back to 2026-03-22 in `git log`.
