# Execution Log: YYYY-MM-DD - [Description]

> **Status**: IN PROGRESS
> **Objective**: [Goal]

---

## Environment Configuration

```bash
#!/bin/bash
source ../../local-only/auth-token.sh

export BASE_URL="https://admin.hlx.page"
export ORG="org-name"
export SITE="site-name"
export REF="main"

echo "Configuring for: ${ORG}/${SITE}"
```

---

## Step 1: Get Current Config (GET) - TODO

**OBJECTIVE**: Fetch current state before changes

**Endpoint**: `GET https://admin.hlx.page/config/{ORG}/sites/{SITE}.json`

```bash
source .env-setup.sh

HTTP_STATUS=$(curl -s --request GET \
  --url "${BASE_URL}/config/${ORG}/sites/${SITE}.json" \
  --header "X-Auth-Token: ${AUTH_TOKEN}" \
  -o execution-files/step-1.1-get-config-response.json \
  -w "%{http_code}")
echo "HTTP Status: ${HTTP_STATUS}"
cat execution-files/step-1.1-get-config-response.json | jq
```

**Response File**: [execution-files/step-1.1-get-config-response.json](execution-files/step-1.1-get-config-response.json)

**Result**: [pending]

**Validation**:
- [ ] HTTP 200 status returned
- [ ] Valid JSON response

---

## Step 2: Update Config (POST) - TODO

**OBJECTIVE**: Apply changes

**Endpoint**: `POST https://admin.hlx.page/config/{ORG}/sites/{SITE}/resource.json`

**Request Payload**: [execution-files/step-2.1-set-resource-request.json](execution-files/step-2.1-set-resource-request.json)

```bash
source .env-setup.sh

HTTP_STATUS=$(curl -s --request POST \
  --url "${BASE_URL}/config/${ORG}/sites/${SITE}/resource.json" \
  --header "Content-Type: application/json" \
  --header "X-Auth-Token: ${AUTH_TOKEN}" \
  --data @execution-files/step-2.1-set-resource-request.json \
  -o execution-files/step-2.2-set-resource-response.json \
  -w "%{http_code}")
echo "HTTP Status: ${HTTP_STATUS}"
cat execution-files/step-2.2-set-resource-response.json | jq
```

**Response File**: [execution-files/step-2.2-set-resource-response.json](execution-files/step-2.2-set-resource-response.json)

**Result**: [pending]

**Validation**:
- [ ] HTTP 200 status returned
- [ ] Changes reflected in response

---

## Step 3: Verify Config (GET) - TODO

**OBJECTIVE**: Confirm changes persisted

**Endpoint**: `GET https://admin.hlx.page/config/{ORG}/sites/{SITE}/resource.json`

```bash
source .env-setup.sh

HTTP_STATUS=$(curl -s --request GET \
  --url "${BASE_URL}/config/${ORG}/sites/${SITE}/resource.json" \
  --header "X-Auth-Token: ${AUTH_TOKEN}" \
  -o execution-files/step-3.1-get-verify-resource-response.json \
  -w "%{http_code}")
echo "HTTP Status: ${HTTP_STATUS}"
cat execution-files/step-3.1-get-verify-resource-response.json | jq
```

**Response File**: [execution-files/step-3.1-get-verify-resource-response.json](execution-files/step-3.1-get-verify-resource-response.json)

**Result**: [pending]

**Validation**:
- [ ] HTTP 200 status returned
- [ ] Changes match Step 2 request payload

---

## Completion Checklist

- [ ] Step 1: GET current config
- [ ] Step 2: POST update config
- [ ] Step 3: GET verify config
