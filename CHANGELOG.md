# Changelog

What changed in each release of ai-builder-kit, newest first. One version covers the whole repo: it lives in `plugin.json`, `.codex-plugin/plugin.json` and the top of `.claude-plugin/marketplace.json`, and each release is tagged `vX.Y.Z` in git.

Installs do not wait for a release. Skill entries carry no version, so every push to `main` that touches a skill reaches users on their next update (see "Keeping it up to date" in [README.md](README.md)). A release is a checkpoint that says what those pushes added up to.

- **Major**: a skill changes behavior that users have to know about, such as a `!` commit
- **Minor**: a new skill or a new capability in one
- **Patch**: fixes and docs

The guarded hook plugin keeps its own version in `plugins/hlx-admin-api-executor-guarded/.claude-plugin/plugin.json`, because its folder only holds a symlink to the skill.

## 2.0.0 - 2026-09-13

First release with a version number, set when the repo became a Codex marketplace as well (`plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`). Added the `excalidraw` and `podcast-slides-video` skills.

Skills: `ai-knowledge-harvester`, `branded-pptx`, `chat-conversation-logger`, `competing-pr-triage`, `conversation-logger`, `drawio`, `excalidraw`, `hlx-admin-api-executor`, `jack-git-commit`, `playwright-demo-video`, `podcast-slides-video`. Plugin: `hlx-admin-api-executor-guarded` 1.0.0.

Before 2.0.0 the repo had no version. Its history goes back to 2026-03-22 in `git log`.
