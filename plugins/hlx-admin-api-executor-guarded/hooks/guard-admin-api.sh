#!/usr/bin/env bash
# guard-admin-api.sh
# PreToolUse hook: guards curl POST/PUT/DELETE/PATCH to admin.hlx.page
# Returns "ask" decision so Claude Code prompts user for yes/no approval.
#
# Fails open: if parsing fails, the command is allowed through.

set -euo pipefail

COMMAND=$(jq -r '.tool_input.command // ""')

# If extraction failed, allow (fail-open)
if [ -z "$COMMAND" ]; then
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
  URL_TARGET=$(echo "$COMMAND" | grep -oiE '(admin\.hlx\.page|BASE_URL)[^ ]*' | head -1)

  jq -n \
    --arg method "$METHOD" \
    --arg target "${URL_TARGET:-admin.hlx.page}" \
    '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "ask",
        permissionDecisionReason: ("[HLX Admin API Guard] " + $method + " request to " + $target + ". This is a destructive admin API operation. Approve?")
      }
    }'
  exit 0
fi

# Not a destructive admin API call - allow
exit 0
