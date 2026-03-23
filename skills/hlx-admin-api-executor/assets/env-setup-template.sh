#!/bin/bash
# ============================================
# EXECUTION: YYYY-MM-DD - [Description]
# ============================================

# Source auth token from shared location
source ../../local-only/auth-token.sh

# AEM Admin API Configuration
export BASE_URL="https://admin.hlx.page"
export ORG="org-name"
export SITE="site-name"
export REPO="repo-name"
export REF="main"

# Verify setup
echo "================================================"
echo "Execution: [Description]"
echo "================================================"
echo "Organization: ${ORG}"
echo "Site:         ${SITE}"
echo "Repository:   ${REPO}"
echo "Branch:       ${REF}"
echo "API Base:     ${BASE_URL}"
echo "Auth token:   ${AUTH_TOKEN:0:10}..."
echo "================================================"
