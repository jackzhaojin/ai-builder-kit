# Sample Input for Draw.io Diagram Generation

Use this as a source-markdown template when preparing a diagram request.

## 1) Executive Summary

Build an architecture diagram for a customer support platform with three subsystem frames: Client Apps, Core Platform, and External Providers. Show one shared data store and one optional provider dependency.

## 2) Diagram Intent

- **Diagram type:** Architecture
- **Complexity:** Medium (~18 boxes)
- **Primary reading direction:** Left-to-right between frames, top-to-bottom inside each frame
- **Color semantic axis:** Determinism (default palette)

## 3) Subsystems / Frames

### Frame A — Client Apps
- Web App (owned by Product)
- Mobile App (owned by Product)
- Admin Console (owned by Support Ops)

### Frame B — Core Platform
- API Gateway (owned by Platform)
- Auth Service (owned by Platform)
- Ticket Service (owned by Platform)
- Notification Worker (owned by Platform)
- **Ticket DB** (persistent data store)

### Frame C — External Providers
- Email Provider (third-party vendor)
- SMS Provider (third-party vendor, optional fallback)
- CRM Sync Target (third-party vendor)

## 4) Components (with roles)

For each component, list:
- **Role:** What it does
- **Owner:** Team/vendor
- **Interface/protocol:** HTTP, async queue, webhook, etc.
- **Dependencies:** Upstream/downstream components
- **Notes:** Optionality, uncertainty, exceptions

## 5) Connections

1. Web App → API Gateway (HTTP)
2. Mobile App → API Gateway (HTTP)
3. Admin Console → API Gateway (HTTP)
4. API Gateway → Auth Service (token verify)
5. API Gateway → Ticket Service (create/update ticket)
6. Ticket Service → Ticket DB (write/read)
7. Ticket Service → Notification Worker (enqueue event)
8. Notification Worker → Email Provider (primary outbound)
9. Notification Worker → SMS Provider (fallback outbound, optional)
10. Ticket Service → CRM Sync Target (async sync)
11. Auth Service → API Gateway (response/decision)

## 6) Cross-Cutting Concerns

- Login/auth applies to all client-originating requests.
- Telemetry and audit logging apply to Core Platform services.
- External providers are third-party and not owned by Platform.

## 7) Style Hints

- Use swimlane frames for each subsystem.
- Use rounded rectangles for services/components.
- Use a **cylinder** for `Ticket DB`.
- Use dashed connectors only for **response/return direction**.
- Unknown/optional relationship: annotate with `?` in edge label (no dashed ambiguity).

## 8) Validation Notes

- No edge should cross through non-endpoint boxes.
- Converging arrows into the same target should share one bind point.
- Include legend because 2+ semantic colors are present.

