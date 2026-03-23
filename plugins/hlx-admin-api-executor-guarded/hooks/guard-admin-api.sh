#!/usr/bin/env bash
# guard-admin-api.sh
# PreToolUse hook: blocks curl POST/PUT/DELETE/PATCH to admin.hlx.page
# Returns deny decision so Claude Code prompts user for confirmation.
#
# Fails open: if parsing fails, the command is allowed through.

set -euo pipefail

INPUT=$(cat)

# Extract command from tool_input using python3 (ships on macOS/Linux)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

# If extraction failed, allow (fail-open)
if [ -z "$COMMAND" ]; then
  echo '{}'
  exit 0
fi

# Check for destructive curl targeting admin.hlx.page or ${BASE_URL}
IS_DESTRUCTIVE=false

if echo "$COMMAND" | grep -qiE 'curl\b'; then
  if echo "$COMMAND" | grep -qiE '(--request|-X)\s+(POST|PUT|DELETE|PATCH)'; then
    if echo "$COMMAND" | grep -qiE '(admin\.hlx\.page|\$\{?BASE_URL\}?)'; then
      IS_DESTRUCTIVE=true
    fi
  fi
fi

if [ "$IS_DESTRUCTIVE" = true ]; then
  METHOD=$(echo "$COMMAND" | grep -oiE '(--request|-X)\s+(POST|PUT|DELETE|PATCH)' | head -1 | awk '{print toupper($NF)}')

  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny"
  },
  "systemMessage": "[HLX Admin API Guard] Blocked ${METHOD} request to admin.hlx.page. Present the Change Justification (WHY/WHAT/HOW) as described in the skill workflow, then ask for explicit user approval before retrying."
}
EOF
  exit 0
fi

# Not a destructive admin API call - allow
echo '{}'
exit 0
