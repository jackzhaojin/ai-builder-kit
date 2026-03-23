#!/usr/bin/env bash
# guard-admin-api.sh
# PreToolUse hook: guards curl POST/PUT/DELETE/PATCH to admin.hlx.page
# Returns "ask" decision so Claude Code prompts user for yes/no approval.
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

  # Extract the URL target for the reason message
  URL_TARGET=$(echo "$COMMAND" | grep -oiE '(admin\.hlx\.page|BASE_URL)[^ ]*' | head -1)

  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "[HLX Admin API Guard] ${METHOD} request to ${URL_TARGET:-admin.hlx.page}. This is a destructive admin API operation. Approve?"
  }
}
EOF
  exit 0
fi

# Not a destructive admin API call - allow
echo '{}'
exit 0
