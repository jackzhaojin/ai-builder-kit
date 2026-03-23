# AEM Admin API Endpoint Reference

Complete endpoint catalog for `https://admin.hlx.page`. All endpoints return standard error codes: 400 (invalid), 401 (unauthenticated), 403 (forbidden), 404 (not found), 429 (rate limited), 500 (server error), 503 (upstream timeout).

## Table of Contents

- [Status Operations](#status-operations)
- [Preview Operations](#preview-operations)
- [Live/Publish Operations](#livepublish-operations)
- [Code Operations](#code-operations)
- [Cache Operations](#cache-operations)
- [Index Operations](#index-operations)
- [Sitemap Operations](#sitemap-operations)
- [Snapshot Operations](#snapshot-operations)
- [Job Polling](#job-polling)
- [Site Configuration](#site-configuration)
- [Access Configuration](#access-configuration)
- [Path Configuration](#path-configuration)
- [Organization & Users](#organization--users)
- [Secrets & Tokens](#secrets--tokens)
- [Config Versioning](#config-versioning)
- [Profile Configuration](#profile-configuration)
- [Response Schemas](#response-schemas)
- [Common Payloads](#common-payloads)

---

## Status Operations

| Method | Endpoint | Query Params | Auth |
|--------|----------|-------------|------|
| GET | `/status/{org}/{site}/{ref}/{path}` | `editUrl` (optional) | None or AuthCookie |
| POST | `/status/{org}/{site}/{ref}/*` | — | None or AuthCookie |

**Bulk status POST body**:
```json
{
  "paths": ["/path1", "/path2"],
  "forceAsync": false,
  "select": ["edit", "preview", "live"],
  "pathsOnly": false
}
```
Returns 202 with job.

---

## Preview Operations

| Method | Endpoint | Query Params | Auth |
|--------|----------|-------------|------|
| GET | `/preview/{org}/{site}/{ref}/{path}` | — | AuthCookie |
| POST | `/preview/{org}/{site}/{ref}/{path}` | `forceUpdateRedirects` | AuthCookie |
| DELETE | `/preview/{org}/{site}/{ref}/{path}` | — | AuthCookie |
| POST | `/preview/{org}/{site}/{ref}/*` | — | AuthCookie |

**Bulk preview POST body**:
```json
{
  "paths": ["/path1", "/path2"],
  "forceUpdate": false,
  "forceAsync": false,
  "delete": false
}
```
Returns 202 with job.

---

## Live/Publish Operations

| Method | Endpoint | Query Params | Auth |
|--------|----------|-------------|------|
| GET | `/live/{org}/{site}/{ref}/{path}` | — | AuthCookie |
| POST | `/live/{org}/{site}/{ref}/{path}` | `forceUpdateRedirects`, `disableNotifications` | AuthCookie |
| DELETE | `/live/{org}/{site}/{ref}/{path}` | `disableNotifications` | AuthCookie |
| POST | `/live/{org}/{site}/{ref}/*` | — | AuthCookie |

**Bulk publish POST body**:
```json
{
  "paths": ["/path1", "/path2"],
  "forceUpdate": false,
  "forceAsync": false,
  "delete": false
}
```
Returns 202 with job.

---

## Code Operations

| Method | Endpoint | Query Params | Auth |
|--------|----------|-------------|------|
| GET | `/code/{owner}/{repo}/{ref}/{path}` | `branch` | None or AuthCookie |
| POST | `/code/{owner}/{repo}/{ref}/{path}` | `branch` | None or AuthCookie |
| DELETE | `/code/{owner}/{repo}/{ref}/{path}` | `branch` | AuthCookie |
| POST | `/code/{owner}/{repo}/{ref}` | `tag` (true/false) | None or AuthCookie |

**Bulk code POST body**:
```json
{
  "source": "string",
  "baseRef": "string",
  "changes": [
    {
      "type": "string",
      "path": "string",
      "time": "string",
      "commit": "string",
      "contentType": "string"
    }
  ]
}
```

Note: Code endpoints use `{owner}/{repo}` instead of `{org}/{site}`.

---

## Cache Operations

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/cache/{org}/{site}/{ref}/{path}` | None or AuthCookie |

Purges CDN cache for the specified path.

---

## Index Operations

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/index/{org}/{site}/{ref}/{path}` | None or AuthCookie |
| POST | `/index/{org}/{site}/{ref}/{path}` | None or AuthCookie |
| DELETE | `/index/{org}/{site}/{ref}/{path}` | None or AuthCookie |
| POST | `/index/{org}/{site}/{ref}/*` | AuthCookie |

**Bulk index POST body**:
```json
{
  "paths": ["/path1", "/path2"]
}
```
Returns 202 with job.

---

## Sitemap Operations

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/sitemap/{org}/{site}/{ref}/{path}` | None |

Triggers sitemap generation. Returns 200 or 204.

---

## Snapshot Operations

| Method | Endpoint | Body | Auth |
|--------|----------|------|------|
| GET | `/snapshot/{org}/{site}/main` | — | AuthCookie |
| GET | `/snapshot/{org}/{site}/main/{snapshotId}` | — | AuthCookie |
| POST | `/snapshot/{org}/{site}/main/{snapshotId}` | `locked`, `title`, `descr` | AuthCookie |
| DELETE | `/snapshot/{org}/{site}/main/{snapshotId}` | — | AuthCookie |
| GET | `/snapshot/{org}/{site}/main/{snapshotId}/status` | — | AuthCookie |

### Snapshot Resources

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/snapshot/{org}/{site}/main/{snapshotId}/{path}` | AuthCookie |
| DELETE | `/snapshot/{org}/{site}/main/{snapshotId}/{path}` | AuthCookie |
| POST | `/snapshot/{org}/{site}/main/{snapshotId}/*` | AuthCookie |

**Bulk snapshot POST body**:
```json
{
  "paths": ["/path1", "/path2"],
  "forceAsync": false
}
```
Returns 202 with job.

### Snapshot Publishing

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/snapshot/{org}/{site}/main/{snapshotId}/{path}/publish` | AuthCookie |
| POST | `/snapshot/{org}/{site}/main/{snapshotId}/publish` | AuthCookie |

### Snapshot Review

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/snapshot/{org}/{site}/main/{snapshotId}/review` | AuthCookie |

**Lock/unlock notes**: Locking requires `preview:write` permission; unlocking requires `live:write` permission.

---

## Job Polling

Bulk operations (preview/*, live/*, index/*, snapshot/*) return 202 with a job object.

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/job/{org}/{site}/{ref}` | AuthCookie |
| GET | `/job/{org}/{site}/{ref}/{topic}/{jobName}` | AuthCookie |
| GET | `/job/{org}/{site}/{ref}/{topic}/{jobName}/details` | AuthCookie |
| DELETE | `/job/{org}/{site}/{ref}/{topic}/{jobName}` | AuthCookie |

**Job response format (202)**:
```json
{
  "status": 202,
  "messageId": "uuid",
  "job": {
    "topic": "string",
    "name": "string",
    "state": "created|running|completed|failed",
    "startTime": "ISO-8601",
    "data": {}
  },
  "links": {
    "self": "url",
    "list": "url"
  }
}
```

Poll the job `self` link until `state` is `completed` or `failed`.

---

## Site Configuration

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/config/{org}/sites/{site}.json` | Full site config |
| POST | `/config/{org}/sites/{site}.json` | Update site config |
| PUT | `/config/{org}/sites/{site}.json` | Create site |
| DELETE | `/config/{org}/sites/{site}.json` | Delete site (irreversible) |
| GET | `/config/{org}/sites.json` | List all sites |
| GET | `/config/{org}/sites/{site}/versions/{N}.json` | Config at version N |

### Robots.txt

| Method | Endpoint |
|--------|----------|
| GET | `/config/{org}/sites/{site}/robots.txt` |
| POST | `/config/{org}/sites/{site}/robots.txt` |

**IMPORTANT**: Robots.txt uses `Content-Type: text/plain` (not JSON). Send raw text with `--data-binary`. Response echoes the content back as plain text.

---

## Access Configuration

| Method | Endpoint | Scope |
|--------|----------|-------|
| GET/POST | `/config/{org}/sites/{site}/access/admin.json` | Admin roles (config_admin, author, publish) |
| GET/POST | `/config/{org}/sites/{site}/access/site.json` | Site access (email allow-list + tokens) - protects .aem.page AND .aem.live |
| GET/POST | `/config/{org}/sites/{site}/access/preview.json` | Preview-only access (.aem.page) |
| GET/POST | `/config/{org}/sites/{site}/access/live.json` | Live-only access (.aem.live) |

**WARNING**: POST replaces the entire access config. Always GET first, merge, then POST.

---

## Path Configuration

| Method | Endpoint | Content-Type | Purpose |
|--------|----------|-------------|---------|
| GET/POST | `/config/{org}/sites/{site}/public.json` | application/json | Path mappings + DAM includes |
| GET/PUT | `/config/{org}/sites/{site}/content/query.yaml` | text/yaml | Query index definition |

---

## Organization & Users

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/config/{org}.json` | Organization config |
| POST | `/config/{org}.json` | Update org config |
| PUT | `/config/{org}.json` | Create org |
| DELETE | `/config/{org}.json` | Delete org |
| GET | `/config/{org}/users.json` | List org users |
| POST | `/config/{org}/users.json` | Add user (single user per request) |

**WARNING**: Users endpoint accepts one user object per POST. Array payloads return 400.

---

## Secrets & Tokens

### Secrets

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/config/{org}/sites/{site}/secrets` | List secrets |
| POST | `/config/{org}/sites/{site}/secrets.json` | Create secret (value shown only once) |
| GET | `/config/{org}/sites/{site}/secrets/{secretId}` | Read secret metadata |
| DELETE | `/config/{org}/sites/{site}/secrets/{secretId}` | Delete secret |

### Tokens

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/config/{org}/sites/{site}/tokens` | List tokens |
| POST | `/config/{org}/sites/{site}/tokens` | Create token |
| GET | `/config/{org}/sites/{site}/tokens/{tokenId}` | Read token |
| DELETE | `/config/{org}/sites/{site}/tokens/{tokenId}` | Delete token |

### API Keys

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/config/{org}/sites/{site}/keys` | List keys |
| POST | `/config/{org}/sites/{site}/keys` | Create or import key |
| GET | `/config/{org}/sites/{site}/keys/{keyId}` | Read key |
| DELETE | `/config/{org}/sites/{site}/keys/{keyId}` | Delete key |

---

## Config Versioning

Available at org, site, and profile levels:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/config/{org}/versions` | List config versions |
| GET | `/config/{org}/versions/{versionId}` | Get specific version |
| DELETE | `/config/{org}/versions/{versionId}` | Delete version |
| POST | `/config/{org}/versions/{versionId}/restore` | Restore version |
| GET | `/config/{org}/sites/{site}/versions` | Site-level versions |
| POST | `/config/{org}/sites/{site}/versions/{versionId}/restore` | Restore site version |

---

## Profile Configuration

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/config/{org}/sites/{site}/profile/{profileId}` | Read profile config |
| POST | `/config/{org}/sites/{site}/profile/{profileId}` | Update profile |
| PUT | `/config/{org}/sites/{site}/profile/{profileId}` | Create profile |
| DELETE | `/config/{org}/sites/{site}/profile/{profileId}` | Delete profile |

---

## Response Schemas

### Status Response (200)

```json
{
  "webPath": "/path",
  "resourcePath": "/path.md",
  "live": {
    "status": 200,
    "url": "string",
    "lastModified": "ISO-8601",
    "lastModifiedBy": "email",
    "contentBusId": "string",
    "permissions": ["read", "write"]
  },
  "preview": {
    "status": 200,
    "url": "string",
    "lastModified": "ISO-8601",
    "contentBusId": "string",
    "permissions": ["read", "write"]
  },
  "edit": {
    "status": 200,
    "url": "string",
    "sourceLocation": "string",
    "lastModified": "ISO-8601"
  },
  "code": {
    "status": 404,
    "codeBusId": "string",
    "permissions": ["read"]
  },
  "links": {
    "status": "url",
    "preview": "url",
    "live": "url",
    "code": "url"
  }
}
```

### Code Response (200)

```json
{
  "webPath": "/scripts.js",
  "resourcePath": "/scripts.js",
  "live": { "url": "string" },
  "preview": { "url": "string" },
  "edit": { "url": "string" },
  "code": {
    "status": 200,
    "lastModified": "ISO-8601",
    "sourceLastModified": "ISO-8601",
    "codeBusId": "string",
    "permissions": ["read", "write"]
  }
}
```

### Index Response (200)

```json
{
  "webPath": "/path",
  "resourcePath": "/path.md",
  "index": {
    "name": "index-name",
    "githubLink": "url",
    "indexedUrl": "url",
    "lastModified": "RFC-1123"
  }
}
```

---

## Common Payloads

### Admin access (roles)
```json
{
  "role": {
    "config_admin": ["TECHACCT@techacct.adobe.com"],
    "author": ["*@company1.com", "*@company2.com"],
    "publish": ["user@company.com"]
  },
  "requireAuth": "auto"
}
```

### Site access (email + token)
```json
{
  "allow": ["*@adobe.com", "*@company1.com"],
  "secretId": ["token-id-here"]
}
```

### Path mappings
```json
{
  "paths": {
    "mappings": ["/content/site/:/", "/content/site/us/en:/en-us"],
    "includes": ["/content/site/", "/content/dam/site/"]
  }
}
```

### Config schemas supported
`schemaSiteConfig`, `schemaCDNConfig`, `schemaCodeConfig`, `schemaContentConfig`, `schemaFoldersConfig`, `schemaHeadersConfig`, `schemaMetadataConfig`, `schemaPublicConfig`, `schemaRobotsConfig`, `schemaSidekickConfig`, `schemaTokensConfig`, `schemaSecretsConfig`, `schemaAccessConfig`
