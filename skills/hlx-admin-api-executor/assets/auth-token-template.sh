#!/bin/bash
# ============================================
# AEM ADMIN API AUTHENTICATION TOKEN
# ============================================
# NEVER COMMIT THIS FILE TO VERSION CONTROL
# Add to .gitignore immediately
#
# How to get your token:
# 1. Open https://admin.hlx.page/login/{ORG}/{SITE}/{REF}
# 2. Open DevTools (F12) > Application > Cookies
# 3. Find the auth_token cookie and copy its value
# 4. Paste below
# 5. Token TTL: ~7200 seconds (2 hours)

export AUTH_TOKEN="paste-your-token-here"
