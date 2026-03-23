# hlx-admin-api-executor-guarded

AEM Edge Delivery Services (Helix 5) Admin API executor with enforced guardrails.

## What This Does

Bundles the `hlx-admin-api-executor` skill with a `PreToolUse` hook that **blocks** any destructive `curl` command targeting `admin.hlx.page` before it executes. Claude must present a Change Justification (WHY/WHAT/HOW) and get explicit user approval before the command can run.

## Plugin vs Standalone Skill

| | Standalone Skill | This Plugin |
|---|---|---|
| Workflow guidance | Yes | Yes |
| Endpoint reference | Yes | Yes |
| Execution templates | Yes | Yes |
| **Enforced guardrails** | No (soft instructions only) | **Yes (PreToolUse hook)** |

Use the **standalone skill** when you trust the workflow instructions alone.
Use this **plugin** when you want deterministic enforcement — destructive operations are blocked at the tool level regardless of what the model decides.

## What Gets Blocked

Any `Bash` command containing:
- `curl` with `--request` or `-X` set to `POST`, `PUT`, `DELETE`, or `PATCH`
- Targeting `admin.hlx.page` or `${BASE_URL}` (the standard env var from the skill's `.env-setup.sh`)

GET requests are never blocked.

## Installation

```bash
claude plugin add /path/to/hlx-admin-api-executor-guarded
```

Or copy the entire directory into your project's `.claude/plugins/`.

## Requirements

- `python3` (used by the guard hook for JSON parsing; ships on macOS and most Linux)
