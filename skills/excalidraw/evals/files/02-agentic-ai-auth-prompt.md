Create an ARCHITECTURE diagram showing how different AI agents authenticate to Azure with proper role-based access.

Title: Enabling Agentic AI Agents with Proper Azure Role-Based Access Control

Legend (top-left, mini-row of labeled swatches):
- Green: actor
- Red: actor auth
- Orange: az member
- Blue: az resource

Components by Category:

Actors (green, column 1):
- Local User
- Local github co-pilot
- OpenAI Codex
- Github Action
- Azure Web App

Actor Auth (red, column 2, one per row, aligned with its actor):
- az login (passwordless) — for Local github co-pilot
- tenant, id, secret — for OpenAI Codex
- OIDC (passwordless) — for Github Action
- System Managed ID (passwordless) — for Azure Web App
- (Local User row does NOT have an auth box; it just points directly into Local github co-pilot on the next row down)

Az Members (orange, column 3, one per row, aligned with its auth):
- user identity — for az login row
- service principal - timed secret — for tenant/id/secret row
- service principal - federated — for OIDC row
- System Managed ID — for System Managed ID row

Az Resources (blue, column 4, one per row):
- storage + ai foundry — for az login row
- storage + ai foundry — for tenant/id/secret row
- Azure Webapp — for OIDC row
- storage + ai foundry — for System Managed ID row

Connections:
- Local User -> Local github co-pilot (vertical, across rows)
- Each actor (rows 2-5) -> its auth (horizontal)
- Each auth -> its az member (horizontal)
- Each az member -> its az resource (horizontal)

Layout notes:
- Row-grid: 5 rows × 4 columns.
- All same-row boxes share Y and height.
- All same-column boxes share X and width.
- Boxes are a consistent smaller size (~170x75) because of row density.
- Legend is a small 2x2 mini-grid of colored swatches in the top-left, outside the main flow.
- Title centered across the top of the diagram.
- No frames.

Output: Save as `agentic-ai-auth.excalidraw`
