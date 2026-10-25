#!/usr/bin/env bash
# guard-admin-api.sh
# PreToolUse hook: guards curl writes to the AEM Admin API (admin.hlx.page, api.aem.live or
# ${BASE_URL}). A write is an explicit POST/PUT/DELETE/PATCH (-X POST, -XPOST, --request=DELETE)
# or a request body or upload, which curl sends as POST or PUT (-d, --data*, -F, --form*, --json,
# -T, --upload-file).
# Returns an "ask" decision so Claude Code prompts the user for yes/no approval.
#
# Works as a plugin hook (hooks.json) or on its own: see the plugin README, "Use the hook
# without the plugin".
#
# Fails open: if parsing fails, the command is allowed through.

set -euo pipefail

COMMAND=$(jq -r '.tool_input.command // ""')

# If extraction failed, allow (fail-open)
if [ -z "$COMMAND" ]; then
  exit 0
fi

HOST_RE='(admin\.hlx\.page|api\.aem\.live|\$\{?BASE_URL\}?)'
METHOD_RE="(-X[[:space:]]*|--request[=[:space:]]+)[\"']?(POST|PUT|DELETE|PATCH)"
BODY_RE='(^|[[:space:]])(-d|--data[a-z-]*|-F|--form[a-z-]*|--json)([[:space:]=]|$)'
UPLOAD_RE='(^|[[:space:]])(-T|--upload-file)([[:space:]=]|$)'

# Check for a curl write targeting an Admin API host
METHOD=""

if echo "$COMMAND" | grep -qiE 'curl\b' && echo "$COMMAND" | grep -qiE "$HOST_RE"; then
  if echo "$COMMAND" | grep -qiE "$METHOD_RE"; then
    METHOD=$(echo "$COMMAND" | grep -oiE "$METHOD_RE" | head -1 | grep -oiE '(POST|PUT|DELETE|PATCH)' | tr '[:lower:]' '[:upper:]')
  elif echo "$COMMAND" | grep -qE "$UPLOAD_RE"; then
    METHOD="PUT"
  elif echo "$COMMAND" | grep -qE "$BODY_RE"; then
    METHOD="POST"
  fi
fi

if [ -n "$METHOD" ]; then
  URL_TARGET=$(echo "$COMMAND" | grep -oiE '(admin\.hlx\.page|api\.aem\.live|BASE_URL)[^ "'"'"']*' | head -1)

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
