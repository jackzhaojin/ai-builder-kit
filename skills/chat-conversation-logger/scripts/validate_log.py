#!/usr/bin/env python3
"""
validate_log.py — Structural linter for chat-conversation-logger output.

Checks a generated log file conforms to the format documented in SKILL.md:
  - Filename matches YYYY-MM-DD-HHMM-{slug}.md
  - YAML frontmatter present, parseable, and contains required fields
  - prompt_count matches the actual number of "### Prompt N:" headers
  - Every prompt block has an Inputs line, a verbatim blockquote, and
    Response/Action/Tools triplet lines
  - No obvious "summary creep" (forbidden section headers)

Usage:
    python validate_log.py path/to/log.md

Exit codes:
    0 — log is well-formed (no issues, or warnings only)
    1 — log has one or more errors

Output goes to stdout. Errors prefixed [E], warnings prefixed [W].
This is a sanity check, not a strict gate. Real verbatim-fidelity can only
be checked by a human comparing log to chat.
"""

import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER = {"date", "time", "platform", "topic", "prompt_count", "status"}
ALLOWED_STATUS = {"complete", "in-progress", "blocked", "exploration"}
FORBIDDEN_HEADERS = {
    "## what was built",
    "## key decisions",
    "## next steps",
    "## accomplishments",
    "## summary of changes",
}
FILENAME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}-[a-z0-9-]+\.md$")
PROMPT_HEADER = re.compile(r"^### Prompt (\d+):\s*(.+)$", re.MULTILINE)


def parse_frontmatter(content):
    """Pull the YAML frontmatter dict from a markdown file. Returns (dict, body) or (None, None)."""
    if not content.startswith("---\n"):
        return None, None
    end = content.find("\n---\n", 4)
    if end == -1:
        return None, None
    raw = content[4:end]
    body = content[end + 5:]
    fm = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, body


def check_filename(path, errors, warnings):
    name = path.name
    if not FILENAME_PATTERN.match(name):
        errors.append(
            f"filename '{name}' does not match YYYY-MM-DD-HHMM-{{slug}}.md pattern"
        )


def check_frontmatter(fm, errors, warnings):
    if fm is None:
        errors.append("missing or unparseable YAML frontmatter")
        return
    missing = REQUIRED_FRONTMATTER - set(fm.keys())
    if missing:
        errors.append(f"frontmatter missing required field(s): {sorted(missing)}")
    if fm.get("platform") and fm["platform"] != "claude-ai":
        warnings.append(f"frontmatter platform is '{fm['platform']}', expected 'claude-ai'")
    status = fm.get("status")
    if status and status not in ALLOWED_STATUS:
        warnings.append(
            f"status '{status}' is not one of {sorted(ALLOWED_STATUS)}"
        )
    pc = fm.get("prompt_count")
    if pc is not None:
        try:
            int(pc)
        except ValueError:
            errors.append(f"prompt_count '{pc}' is not an integer")


def check_prompt_blocks(body, fm, errors, warnings):
    headers = list(PROMPT_HEADER.finditer(body))
    if not headers:
        warnings.append("no '### Prompt N:' headers found — is this an empty session log?")
        return

    # Numbering check
    numbers = [int(m.group(1)) for m in headers]
    if numbers != list(range(1, len(numbers) + 1)):
        errors.append(
            f"prompt numbers are not sequential 1..N: got {numbers}"
        )

    # prompt_count match
    if fm and fm.get("prompt_count"):
        try:
            declared = int(fm["prompt_count"])
            if declared != len(headers):
                errors.append(
                    f"frontmatter prompt_count={declared} but found {len(headers)} prompt headers"
                )
        except ValueError:
            pass  # already reported

    # Per-block structural check
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        block = body[start:end]
        n = m.group(1)

        if "**Inputs**:" not in block:
            errors.append(f"Prompt {n}: missing '**Inputs**:' line")
        if not re.search(r"^>\s+\S", block, re.MULTILINE):
            errors.append(f"Prompt {n}: missing verbatim blockquote (lines starting with '> ')")
        if "→ Response:" not in block:
            errors.append(f"Prompt {n}: missing '→ Response:' line")
        if "→ Action:" not in block:
            errors.append(f"Prompt {n}: missing '→ Action:' line")
        if "→ Tools:" not in block:
            errors.append(f"Prompt {n}: missing '→ Tools:' line")


def check_summary_creep(body, warnings):
    lower = body.lower()
    for forbidden in FORBIDDEN_HEADERS:
        if forbidden in lower:
            warnings.append(
                f"forbidden summary-style header found: '{forbidden}'. "
                "The prompts are the record — don't duplicate them in summary form."
            )


def validate(path):
    path = Path(path)
    if not path.exists():
        print(f"[E] file not found: {path}")
        return 1
    if not path.is_file():
        print(f"[E] not a file: {path}")
        return 1

    content = path.read_text(encoding="utf-8")
    errors = []
    warnings = []

    check_filename(path, errors, warnings)
    fm, body = parse_frontmatter(content)
    check_frontmatter(fm, errors, warnings)
    if body is not None:
        check_prompt_blocks(body, fm, errors, warnings)
        check_summary_creep(body, warnings)

    for w in warnings:
        print(f"[W] {w}")
    for e in errors:
        print(f"[E] {e}")

    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) — log has issues")
        return 1
    if warnings:
        print(f"\n0 errors, {len(warnings)} warning(s) — log is acceptable")
        return 0
    print("✅ log is well-formed")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_log.py <path-to-log.md>", file=sys.stderr)
        sys.exit(2)
    sys.exit(validate(sys.argv[1]))
