---
name: hlx-admin-api-executor
description: "Interactive AEM Edge Delivery Services (EDS/Helix 5) Admin API executor with human-in-the-loop oversight. Use when working with the AEM Admin API (admin.hlx.page) to: (1) Plan and execute admin operations step-by-step (preview, publish, config, access, cache, index, snapshots, code), (2) Execute ONE API request at a time with human review and approval, (3) Document all requests/responses in EXECUTION.md with full traceability, (4) Follow GET/SET/GET verification patterns for safe configuration changes, (5) Resume existing executions and add new steps, (6) Manage site configuration, access control, content operations, and code deployments. For careful AEM admin operations where mistakes are costly - NOT for bulk automation."
---

# HLX Admin API Executor

Execute AEM Edge Delivery Services (Helix 5) Admin API workflows with interactive planning, human-in-the-loop approval, and full request/response documentation. **One operation at a time** for careful admin work.

## Execution Philosophy

**Single-Step Execution**: Execute ONE operation at a time with full human oversight. Each step is planned, executed individually, verified, and documented. This is for serious admin operations where mistakes are costly.

## Mode Selection

Determine mode first:

- **New**: No existing EXECUTION.md. Follow Phases 1-4.
- **Resume**: Existing EXECUTION.md provided. Read it, identify last completed step, ask what to do next (continue / add step / retry / verify).

When resuming, never overwrite existing steps. Append with correct numbering. Preserve all previous files.

## Authentication

**Header**: `X-Auth-Token: ${AUTH_TOKEN}`

Obtain token:
1. Open `https://admin.hlx.page/login/{ORG}/{SITE}/{REF}` in browser
2. Extract `auth_token` cookie from DevTools > Application > Cookies
3. Save to `local-only/auth-token.sh`
4. TTL: ~7200 seconds (2 hours)

Verify: `GET https://admin.hlx.page/profile` with `X-Auth-Token` header.

**Site tokens** use a different header: `Authorization: token hlx_...` (not X-Auth-Token).

## Environment Variables

```bash
export BASE_URL="https://admin.hlx.page"
export ORG="my-org"        # GitHub organization
export SITE="my-site"      # Site identifier
export REPO="my-repo"      # Code repository
export REF="main"          # Git branch
```

## URL Patterns

| Environment | Pattern |
|-------------|---------|
| Admin API | `https://admin.hlx.page/...` |
| Preview | `https://{REF}--{SITE}--{ORG}.aem.page/{path}` |
| Live | `https://{REF}--{SITE}--{ORG}.aem.live/{path}` |

## Endpoint Reference

For the full endpoint catalog with parameters, response schemas, and job polling details, read [references/endpoints.md](references/endpoints.md).

## Critical Quirks

1. **POST overwrites entire config**: Access endpoints (`access/admin.json`, `access/site.json`, etc.) replace the entire config on POST. Always GET first, merge changes, then POST the complete payload.
2. **Single user per POST**: `/config/{ORG}/users.json` accepts one user object only. Array payloads return 400.
3. **Site token shown once**: `POST /config/{ORG}/sites/{SITE}/secrets.json` returns the token value only on creation. Record immediately.
4. **Bulk ops return 202**: Preview/publish/index bulk operations return 202 with a job URL. Poll `GET /job/{ORG}/{SITE}/{REF}/{topic}/{jobName}` until `state` is `completed` or `failed`.
5. **Config auto-reset risk**: AEM technical accounts may push config during bulk operations from AEM Sites Console, reverting changes. Verify config after bulk operations.
6. **Version tracking**: Every config change increments the version. Use `/config/{ORG}/sites/{SITE}/versions/{N}.json` for auditing or recovery.
7. **Rate limits**: 429 responses when exceeded. Content source operations (preview with `?edit=auto`) are subject to SharePoint/Google Docs rate limits (503 on timeout).

## Folder Structure

```
{site-or-project}/
└── YYYY-MM-DD-description/
    ├── EXECUTION.md
    ├── .env-setup.sh
    └── execution-files/
        ├── step-1.1-get-description-response.json
        ├── step-2.1-set-description-request.json
        ├── step-2.2-set-description-response.json
        └── step-3.1-get-verify-description-response.json
```

## Step Numbering

Use decimal sub-steps: `.1` for request payload, `.2` for response. GET-only steps have one sub-step (`.1` for response).

## Workflow

### Phase 1: Planning

Ask:
1. What's the goal?
2. What org/site/ref?
3. What resources are involved?
4. What's the sequence? Suggest GET/SET/GET pattern.
5. Where to save files? Suggest `YYYY-MM-DD-description/`.

### Phase 2: Generate Plan

Create EXECUTION.md with steps as TODO. Each step includes:
- **OBJECTIVE**: What it accomplishes
- **Endpoint**: Full URL with method
- **Command**: Complete curl using env vars and `@file` references
- **Acceptance Criteria**: What success looks like
- **Validation**: Checkbox list

Create `.env-setup.sh` with all needed variables. Show plan for approval.

### Phase 3: Execution

**Execute ONE step at a time. Wait for user confirmation between steps.**

#### GET Requests

```bash
source .env-setup.sh

HTTP_STATUS=$(curl -s --request GET \
  --url "${BASE_URL}/config/${ORG}/sites/${SITE}.json" \
  --header "X-Auth-Token: ${AUTH_TOKEN}" \
  -o execution-files/step-1.1-get-site-config-response.json \
  -w "%{http_code}")
echo "HTTP Status: ${HTTP_STATUS}"
cat execution-files/step-1.1-get-site-config-response.json | jq
```

#### POST/PUT/DELETE (Require Human Review)

**Every non-GET request requires human review with a justification block before execution.**

1. Save request payload to `execution-files/step-N.1-...-request.json`
2. Present the **Change Justification** block (see format below)
3. Show curl command referencing `@file` and the file path
4. Wait for explicit "Yes" before executing
5. Never inline request body in approval prompt

**On failure**: If a POST/PUT/DELETE returns a non-2xx status, **do NOT automatically retry or fix the request**. Instead:
1. Report the failure (status code, response body) to the user
2. Investigate the root cause (wrong content type, malformed payload, missing fields, etc.)
3. Present the proposed fix as a new Change Justification block with WHY/WHAT/HOW
4. Wait for explicit human approval before executing the corrected request

This applies even when the fix is obvious. The human must review every mutation attempt.

**Approval format with justification**:
```
## Change Review: Step N — [Description]

### WHY
Why is this change needed? What problem does it solve or what goal does it advance?

### WHAT
What exactly is being changed? Describe the before → after state.
Reference the current state from the preceding GET step.

### HOW
How is the change applied? Which endpoint, method, and payload fields are involved?
Call out any side effects (e.g., "POST replaces entire config — all existing fields preserved").

---

Endpoint: POST https://admin.hlx.page/config/{ORG}/sites/{SITE}/access/admin.json

Request payload saved to:
  execution-files/step-N.1-set-access-admin-request.json

Command:
  curl -s --request POST \
    --url "${BASE_URL}/config/${ORG}/sites/${SITE}/access/admin.json" \
    --header "Content-Type: application/json" \
    --header "X-Auth-Token: ${AUTH_TOKEN}" \
    --data @execution-files/step-N.1-set-access-admin-request.json \
    -o execution-files/step-N.2-set-access-admin-response.json \
    -w "%{http_code}"

Ready to execute? (Yes / No / Modify)
```

### Phase 4: Documentation

Update EXECUTION.md after each step:
- Mark completed steps with `✅ COMPLETED`
- Record HTTP status and key findings under **Result**
- Check off validation items

## GET/SET/GET Pattern

For every modification, execute in sequence, one step at a time:
1. **GET before** - Capture current state, wait for user
2. **SET** - Apply the change, wait for user
3. **GET after** - Verify persistence, wait for user

**Never execute multiple steps without user confirmation between them.**

## curl Conventions

- `${ENV_VARS}` - never hardcode values
- `-s` for silent mode
- `--request METHOD` explicit method
- `--data @file` for request bodies (never inline in curl)
- `-o execution-files/step-N.N-description.json` for output
- `-w "%{http_code}"` to capture status
- Pipe to `jq` for display

## Roles Reference

| Role | Purpose |
|------|---------|
| `config_admin` | Technical account for API automation |
| `author` | Preview, Sidekick, Universal Editor (no publish) |
| `publish` | All author permissions + publish to live |

## Templates

- **Execution log**: See [assets/execution-template.md](assets/execution-template.md)
- **Auth token**: See [assets/auth-token-template.sh](assets/auth-token-template.sh)
- **Env setup**: See [assets/env-setup-template.sh](assets/env-setup-template.sh)
- **Gitignore**: See [assets/gitignore-template](assets/gitignore-template)
