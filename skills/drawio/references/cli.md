# draw.io CLI Reference

Source: https://github.com/jgraph/drawio-mcp/blob/main/skill-cli/drawio/SKILL.md

The draw.io desktop app includes a CLI for exporting `.drawio` files to PNG, SVG, or PDF.

---

## CLI Location

| Platform | Path |
|----------|------|
| macOS | `/Applications/draw.io.app/Contents/MacOS/draw.io` |
| Linux (native) | `drawio` (typically on PATH via snap/apt/flatpak) |
| Windows | `"C:\Program Files\draw.io\draw.io.exe"` |
| WSL2 | `` `/mnt/c/Program Files/draw.io/draw.io.exe` `` |

Use `which drawio` (or `where drawio` on Windows) to check if it's on PATH before falling back to platform paths.

WSL2 per-user fallback: `/mnt/c/Users/$WIN_USER/AppData/Local/Programs/draw.io/draw.io.exe`

---

## Export Command

```sh
drawio -x -f <format> -b 10 -o <output> <input.drawio>
```

> **⚠️ DO NOT use `-e` / `--embed-diagram`.** It embeds the full diagram XML into the image and breaks Claude Code's image reader (the Read tool cannot parse the resulting PNG). Keep the source `.drawio` file for re-editing instead — see "File Naming Conventions" below.

**Key flags:**
- `-x` / `--export` — export mode
- `-f` / `--format` — output format: `png`, `svg`, `pdf`, `jpg`
- `-o` / `--output` — output file path
- `-b` / `--border` — border width in pixels (default: 0; recommend 10)
- `-t` / `--transparent` — transparent background (PNG only)
- `-s` / `--scale` — scale the diagram size
- `--width` / `--height` — fit into dimensions (preserves aspect ratio)
- `-a` / `--all-pages` — export all pages (PDF only)
- `-p` / `--page-index` — select a specific page (1-based)
- `-e` / `--embed-diagram` — ❌ **do not use**; breaks Claude Code image reading

macOS example:
```sh
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -b 10 -o diagram.png diagram.drawio
```

---

## Supported Export Formats

| Format | Notes |
|--------|-------|
| png | Viewable everywhere, readable by Claude Code's Read tool |
| svg | Scalable vector, text-based, good fallback if PNG ever fails |
| pdf | Printable |
| jpg | Lossy |

Re-editing: keep the source `.drawio` file. Do **not** try to round-trip through an image via `-e` — that flag bloats the PNG and breaks the image reader.

---

## Opening the Result

| Platform | Command |
|----------|---------|
| macOS | `open <file>` |
| Linux (native) | `xdg-open <file>` |
| WSL2 | `cmd.exe /c start "" "$(wslpath -w <file>)"` |
| Windows | `start <file>` |

---

## File Naming Conventions

- Descriptive lowercase with hyphens: `login-flow`, `database-schema`
- For exports, use a single clean extension: `name.png`, `name.svg`, `name.pdf`
- **Keep the source `.drawio` file** alongside the exported image. Without `-e` (which we don't use), the image is not re-editable — the `.drawio` is the source of truth.

---

## Optional: Edge Routing Post-Processing

If `npx @drawio/postprocess` is available, run it on the `.drawio` file before export to optimize edge routing (simplify waypoints, fix edge-vertex collisions, straighten approach angles). Skip silently if not available — do not install it or ask the user about it.

```sh
npx @drawio/postprocess diagram.drawio
```

---

## Workflow When Export is Requested

1. Generate draw.io XML and write to a `.drawio` file
2. (Optional) Run `npx @drawio/postprocess` on the file
3. Locate the CLI (check PATH first, then platform-specific path)
4. Export: `drawio -x -f <format> -b 10 -o <output> <input.drawio>` — **never pass `-e`** (breaks Claude Code image reading)
5. **Keep** the `.drawio` file alongside the exported image — it is the source of truth for future edits
6. Open the result with the platform open command; if it fails, print the absolute file path

If the CLI is not found, keep the `.drawio` file and tell the user to install the draw.io desktop app, or open the file directly.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| CLI not found | Desktop app not installed or not on PATH | Keep `.drawio` file, tell user to install draw.io desktop app |
| Export produces empty/corrupt file | Invalid XML | Validate XML well-formedness before writing |
| Diagram opens but looks blank | Missing root cells id="0" and id="1" | Ensure basic mxGraphModel structure is complete |
| Edges not rendering | Edge mxCell is self-closing (no child mxGeometry) | Every edge must have `<mxGeometry relative="1" as="geometry" />` |
| File won't open after export | Incorrect file path or missing file association | Print the absolute file path so the user can open it manually |
