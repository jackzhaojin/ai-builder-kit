Create a PROCESS diagram showing CMS authoring patterns and how content flows to edge delivery.

Title: (no title in this diagram — rely on column headers)

Column headers (free-floating text, no boxes, one per column):
- Authoring Interface
- Content Storage
- EDS Processing and compiling
- User

Components:
- Document Editor: Traditional Word-style editor
- Document: Resulting doc blob
- Universal Editor (json configs and html5 data attr): AEM Universal Editor
- AEM Nodes: AEM content node tree
- da.live: da.live as an authoring interface
- Adobe's Cloud - Blobs / NoSQL DB?: da.live's storage
- Preview / Publish Listener: Single listener that triggers the build pipeline
- Compile content + code (SSG): Static site generator step
- Edge Delivery: CDN / edge
- Browser / Devices: End user devices

Flow:
- Document Editor -> Document
- Universal Editor -> AEM Nodes
- da.live -> Adobe's Cloud
- Document / AEM Nodes / Adobe's Cloud -> Preview / Publish Listener (convergence into shared trunk)
- Preview / Publish Listener -> Compile content + code (SSG) -> Edge Delivery
- Browser / Devices -> Edge Delivery (User reaches the delivered site)

Layout notes:
- Horizontal assembly line, left to right, single frame-less diagram.
- 3 parallel rows on the left converge into a single trunk at "Preview / Publish Listener".
- Column headers sit above the columns they describe, free-floating text.
- No legend (one color, default black).
- No frames.
- Same box size everywhere (200x100).

Output: Save as `authoring-patterns.excalidraw`
