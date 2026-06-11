---
name: playwright-demo-video
description: |
  Generate polished demo videos from Playwright specs with AI voiceover, captions, and music.
  Use when: creating demo videos for web projects, extracting captions from Playwright specs,
  generating TTS voiceover with ElevenLabs, merging video with freeze-frame timing, adding
  background music, auto-discovering project features to generate demo specs.
  Trigger: "demo video", "playwright demo", "generate demo", "caption extraction",
  "voiceover pipeline", "freeze frame merge", "auto-discover demo".
---

# Playwright Demo Video Skill

Generate end-to-end demo videos (MP4) from Playwright specs with on-screen captions, AI voiceover (ElevenLabs), freeze-frame timing, and background music.

## Data-First Approach (MANDATORY)

**You cannot narrate what doesn't exist.** Before writing any demo script or narration, you MUST verify that the application has real data to show. A demo that says "here are our recipes" while the screen shows "No items found" is a failed demo.

### Stage 0: Data Setup & Discovery

This stage runs BEFORE any recording or script writing. Its purpose is to ensure the app has content worth demoing and to understand what Playwright can actually interact with.

#### Step 1: Verify or Create Data

Before touching Playwright, ensure the database has seed data:

```typescript
// data-check.ts -- run this BEFORE writing any demo spec
import { test, expect } from '@playwright/test';

test('verify app has demo-worthy data', async ({ page }) => {
  // Start by checking the main content pages
  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');

  // Take inventory of what's actually on the page
  const screenshot = await page.screenshot({ path: 'data-check-home.png' });

  // Check for empty states -- these mean we need to seed data
  const emptyIndicators = [
    'No recipes found',
    'No items',
    'No results',
    'Nothing here yet',
    'Get started by',
    'Create your first',
  ];
  const bodyText = await page.locator('body').innerText();
  for (const indicator of emptyIndicators) {
    if (bodyText.includes(indicator)) {
      console.log(`WARNING: Found empty state indicator: "${indicator}"`);
      console.log('You MUST seed data before recording. Run the seed script.');
    }
  }

  // Count visible content items (cards, list items, articles)
  const contentSelectors = [
    'article', '.card', '[data-testid*="card"]',
    '[data-testid*="item"]', '[data-testid*="recipe"]',
    '.recipe-card', '.product-card', '.list-item'
  ];
  for (const selector of contentSelectors) {
    const count = await page.locator(selector).count();
    if (count > 0) {
      console.log(`Found ${count} elements matching "${selector}"`);
    }
  }
});
```

**If the app shows empty states:**
1. Find and run the seed script (`npm run seed`, `npx prisma db seed`, `npx tsx lib/db/seed.ts`, etc.)
2. If no seed script exists, create minimal seed data via the app's API or direct DB inserts
3. Re-run the data check to confirm content now appears
4. **Do NOT proceed to script writing until content is verified**

#### Step 2: Explore What Playwright Can See

Before writing a full demo script, run an **exploration spec** that visits every route and catalogs what's actually rendered:

```typescript
// explore-routes.spec.ts -- discovery, not recording
import { test, expect } from '@playwright/test';

test('explore all routes', async ({ page }) => {
  const routes = ['/', '/recipes', '/search', '/login', '/register', '/favorites', '/profile'];
  const routeReport: Record<string, { status: string; elements: string[]; screenshot: string }> = {};

  for (const route of routes) {
    await page.goto(`http://localhost:3000${route}`);
    await page.waitForLoadState('networkidle');

    // Check for errors
    const hasError = await page.locator('body').innerText()
      .then(text => text.includes('Runtime Error') || text.includes('Application error'));

    // Catalog interactive elements
    const buttons = await page.locator('button').allInnerTexts();
    const links = await page.locator('a').allInnerTexts();
    const forms = await page.locator('form').count();
    const images = await page.locator('img').count();
    const cards = await page.locator('article, .card, [class*="card"]').count();

    const screenshotPath = `explore-${route.replace(/\//g, '_') || 'home'}.png`;
    await page.screenshot({ path: screenshotPath });

    routeReport[route] = {
      status: hasError ? 'ERROR' : 'OK',
      elements: [
        `${buttons.length} buttons: [${buttons.slice(0, 5).join(', ')}]`,
        `${links.length} links`,
        `${forms} forms`,
        `${images} images`,
        `${cards} cards/articles`,
      ],
      screenshot: screenshotPath,
    };
    console.log(`${route}: ${hasError ? 'ERROR' : 'OK'} | ${cards} cards, ${images} images, ${buttons.length} buttons`);
  }

  // Print summary
  console.log('\n=== ROUTE EXPLORATION SUMMARY ===');
  console.log(JSON.stringify(routeReport, null, 2));
});
```

**Use the exploration output to write the demo script.** Only narrate features that the exploration confirmed exist. If a route shows 0 cards, don't write narration about "browsing our collection."

#### Step 3: Build the Demo Script Incrementally

**Do NOT write the entire demo spec at once.** Build it scene by scene, testing each one:

1. **Scene 1 only:** Write the first scene (e.g., landing page), record it, verify the screenshot shows real content
2. **Scene 1+2:** Add the second scene, record again, verify both scenes
3. **Continue until complete:** Each addition is verified before moving on

```typescript
// Build incrementally -- start with just scene 1
test('demo scene 1 - landing page @demo', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');

  // ASSERT content is visible BEFORE writing any caption about it
  const heroSection = page.locator('h1, [data-testid="hero"]').first();
  await expect(heroSection).toBeVisible({ timeout: 10000 });

  // Only NOW describe what's actually on screen
  caption(page, 'Welcome to Recipe Discovery', 3000);
  // ...
});
```

**Rule: Assert, then narrate.** Every caption must be preceded by an assertion that the content it describes is actually visible. The narration is a description of what IS on screen, not what SHOULD be on screen.

### Demo Script Writing Rules

1. **Always call `startTimestampRecording()` as the first line of the test.** This is the single most important step for reliable video-audio sync. Without it, the pipeline uses heuristic timestamp estimation that drifts on demos >60s.
2. **Never assume data exists.** Always assert before narrating.
3. **Never use `.catch(() => {})`.** If an interaction fails, the demo should fail.
3. **Match narration to visuals exactly.** If the page shows 3 recipes, say "3 recipes" not "our collection of recipes."
4. **Test each scene in isolation first.** Don't chain 10 scenes together and hope they all work.
5. **Use specific, observable descriptions.** Instead of "powerful search capabilities," say "searching for pasta dishes" while the search box shows "pasta" and results are filtered.
6. **Size caption hold times to text length.** The voiceover takes longer than you think. Use this formula for `caption()` hold times:
   ```
   holdMs = max(textLength * 80, 3000)
   ```
   Example: "Welcome to Recipe Discovery, a platform for finding and sharing recipes" (72 chars) → `caption(page, text, 5760)` not `caption(page, text, 3000)`. Short captions (< 40 chars) can use 3000ms. Longer narration needs proportionally more time.
7. **Add a closing pause.** The last scene must include `await page.waitForTimeout(5000)` AFTER the final caption to ensure the voiceover finishes before the Playwright recording ends. The merge script adds a tail freeze for safety, but the spec should still provide enough buffer.

## Visual Verification (MANDATORY)

Demo videos are worthless if the screen shows errors while the narration describes features. Every demo recording MUST pass visual verification at three stages: before, during, and after recording. Skipping these checks is not acceptable -- a demo of an error page is worse than no demo at all.

### Stage 1: Pre-Recording Health Check

Before any recording starts, verify the application is actually working:

1. **Start the dev server and confirm it responds:**
   ```bash
   # Start the server (background or via Playwright's webServer config)
   # Then verify it returns 200, not an error page
   curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
   # Must return 200. If 500 or connection refused, fix the app first.
   ```

2. **Navigate to every route the demo will visit and take a screenshot:**
   ```typescript
   // Pre-flight route check -- run BEFORE the demo spec
   const routesToDemo = ['/', '/recipes', '/recipes/1', '/dashboard'];
   for (const route of routesToDemo) {
     await page.goto(`http://localhost:3000${route}`);
     await page.waitForLoadState('networkidle');
     // Screenshot for manual inspection if needed
     await page.screenshot({ path: `preflight-${route.replace(/\//g, '_')}.png` });
   }
   ```

3. **Verify no error states on any route:**
   ```typescript
   // After each navigation in the pre-flight check:
   await expect(page.locator('body')).not.toContainText('Runtime Error');
   await expect(page.locator('body')).not.toContainText('Unhandled Runtime Error');
   await expect(page.locator('body')).not.toContainText('Application error');
   await expect(page.locator('body')).not.toContainText('Internal Server Error');
   await expect(page.locator('body')).not.toContainText('Module not found');
   // Check for Next.js error overlay specifically
   const errorOverlay = page.locator('nextjs-portal');
   await expect(errorOverlay).toHaveCount(0);
   ```

4. **If any route shows errors, FIX THE APP FIRST.** Do not proceed to recording. Common fixes:
   - Run database migrations / seed data
   - Install missing dependencies
   - Set required environment variables
   - Fix Next.js config (image domains, etc.)

### Stage 2: During-Recording Assertions

The generated demo spec MUST include inline assertions. These are not optional.

**After every `page.goto()` or navigation action, add:**
```typescript
// MANDATORY after every navigation
await expect(page.locator('body')).not.toContainText('Runtime Error');
await expect(page.locator('body')).not.toContainText('Unhandled Runtime Error');
await expect(page.locator('body')).not.toContainText('Application error');
```

**Before narrating about visible content, assert it exists:**
```typescript
// BAD: narrate about recipes without checking they are visible
caption(page, 'Here are the recipes in our collection', 3000);

// GOOD: verify content is on screen BEFORE narrating about it
await expect(
  page.locator('[data-testid="recipe-card"], article, .recipe-card, .card').first()
).toBeVisible({ timeout: 10000 });
caption(page, 'Here are the recipes in our collection', 3000);
```

**NEVER use `.catch(() => {})` on demo-critical interactions:**
```typescript
// BAD: silently swallowing click failures means the demo records garbage
await page.click('[data-testid="add-recipe"]').catch(() => {});

// GOOD: if the click fails, the demo fails -- which is correct behavior
await page.click('[data-testid="add-recipe"]');
```

If an interaction is truly optional (e.g., dismissing a cookie banner that may or may not appear), use an explicit conditional instead:
```typescript
// Acceptable for genuinely optional elements
const cookieBanner = page.locator('[data-testid="cookie-dismiss"]');
if (await cookieBanner.isVisible({ timeout: 2000 }).catch(() => false)) {
  await cookieBanner.click();
}
```

### Stage 3: Post-Recording Validation

After recording completes, verify the output video is not blank or corrupted:

1. **Extract sample frames at 25%, 50%, 75% of the video duration:**
   ```bash
   # Get video duration
   DURATION=$(ffprobe -v error -show_entries format=duration \
     -of default=noprint_wrappers=1:nokey=1 demo-final.mp4)

   # Extract frames at 25%, 50%, 75%
   for pct in 25 50 75; do
     TIMESTAMP=$(echo "$DURATION * $pct / 100" | bc -l)
     ffmpeg -ss "$TIMESTAMP" -i demo-final.mp4 -frames:v 1 \
       "validation-frame-${pct}.png" -y
   done
   ```

2. **Verify frames are not blank (all white or all black):**
   ```bash
   # Check pixel variance -- blank frames have near-zero standard deviation
   for frame in validation-frame-*.png; do
     STDDEV=$(ffprobe -v error -select_streams v:0 \
       -show_entries frame_tags=lavfi.signalstats.YAVG \
       -f lavfi -i "movie=${frame},signalstats" \
       -of default=noprint_wrappers=1:nokey=1 2>/dev/null || echo "0")
     echo "$frame: stddev=$STDDEV"
     # If stddev < 5, the frame is likely blank
   done
   ```

3. **Verify video bitrate is reasonable (blank videos have extremely low bitrate):**
   ```bash
   BITRATE=$(ffprobe -v error -show_entries format=bit_rate \
     -of default=noprint_wrappers=1:nokey=1 demo-final.mp4)
   # Bitrate should be > 50000 (50 kb/s). Blank/error videos typically < 10000.
   echo "Video bitrate: $BITRATE bps"
   ```

4. **If any validation fails, do not deliver the video.** Report the failure with screenshots of the extracted frames so the issue is visible.

### Auto-Discover Mode: Additional Requirements

When generating specs via `auto-discover.mjs`, the generated spec MUST include:

- **Navigation assertions** after every `page.goto()` call (the three error text checks above)
- **Content visibility waits** before each caption that references on-screen content: `await page.waitForSelector('<selector>', { timeout: 10000 })` for key content elements
- **No try/catch suppression** around demo-critical interactions (clicks, form fills, navigation). If an interaction that the narration describes fails, the spec must fail loudly so the developer knows the demo is broken.
- **A pre-flight test block** at the start of the spec that visits all routes and asserts no errors before the recording begins

## Common Failure Modes

Known issues that cause demos to record error pages or blank screens:

| Failure Mode | Symptom in Video | Root Cause | Fix |
|-------------|-----------------|------------|-----|
| Database not running | White screen or "connection refused" error overlay | PostgreSQL/MySQL/SQLite not started or not migrated | Start DB service, run `npx prisma migrate dev` or equivalent seed script |
| Unconfigured image domains | "Unhandled Runtime Error" overlay mentioning `next/image` | `next.config.js` missing remote image hostnames in `images.remotePatterns` | Add the domain to `next.config.js` `images.remotePatterns` or `images.domains` |
| Auth required but no test user | Stuck on login page for entire video, narration describes dashboard | App requires authentication but no test user was seeded | Seed a test user, or configure the demo to log in first |
| Missing environment variables | Server crashes on startup, blank page in browser | `.env` or `.env.local` missing required values (`DATABASE_URL`, API keys, etc.) | Copy `.env.example` to `.env.local`, fill in required values |
| Port already in use | Dev server fails to start, Playwright times out | Another process occupying port 3000/5173 | Kill the existing process or configure a different port |
| Missing dependencies | Module not found errors in browser | `npm install` not run after cloning or after changing branches | Run `npm install` in the project directory |
| Stale build cache | Hydration errors or old UI rendering | `.next/` or `dist/` cache from a different branch or config | Delete `.next/` (or `dist/`) and restart the dev server |
| No data seeded | App loads but shows "No items found" or empty lists for the entire demo | Database is running but has no seed data | Run the seed script (`npx prisma db seed`, `npm run seed`, etc.) |
| Voiceover cut off | Narration abruptly stops mid-sentence near the end of the video | Playwright recording ends before voiceover finishes; `caption()` hold times too short for text length | Use `holdMs = max(textLength * 80, 3000)` for caption timing; add 5s `waitForTimeout` after the final caption; the merge script's tail-freeze handles edge cases automatically |
| **Video freezes, audio continues** | Video shows the same frame for the last 30-50% while voiceover keeps narrating different content | **Multiple `@demo` specs ran during `--record`.** The `--grep @demo` pattern matched all specs, mixing their `__CAPTION_TS__` markers into one log. Captions from later specs have timestamps beyond the first spec's video. The merge freezes the last frame to fit the extra audio. | Use `--grep "Exact Test Name"` to run only one spec. Or after recording, trim `captions.json` to only the target spec's entries and use the per-test video from `test-results/<test-name>/video.webm`. |
| Wrong video for captions | Video shows content from a different demo while narration describes the intended demo | `findRecordedVideo()` picks the most recently modified `.webm` in `test-results/`. When multiple tests run, it picks the LAST test's video, not the intended one. | Pass `--video <path>` explicitly to skip auto-discovery. Find the correct per-test video in `test-results/<test-folder>/video.webm`. |

When any of these are detected during the pre-recording health check (Stage 1), fix the underlying issue before proceeding. Do not attempt to record a demo of a broken application.

## Critical: Multiple `@demo` Specs (MUST READ)

**The `--spec` flag does NOT filter which Playwright tests run.** It only controls caption extraction. The `--grep` flag (default: `@demo`) controls test execution. If multiple spec files contain `@demo` in their test name, ALL of them run during `--record`.

### The Problem

When a project has multiple demo specs (e.g., `auth-demo.spec.ts`, `executive-demo.spec.ts`, `v121-demo.spec.ts`) all tagged `@demo`:

1. `--record` runs ALL of them sequentially via `--grep @demo`
2. ALL `__CAPTION_TS__` markers from ALL tests end up in `recording.log`
3. `captions.json` includes entries from ALL tests (e.g., 86 entries when only 52 belong to the target spec)
4. `findRecordedVideo()` picks the MOST RECENT video — likely the LAST test, not the intended one
5. The merge creates a mismatched video: wrong visuals + wrong audio timing

### Prevention: Use Specific `--grep` Patterns

```bash
# BAD: matches ALL @demo specs
node run-pipeline.mjs --record --spec demo/auth-demo.spec.ts --grep @demo

# GOOD: matches only the specific test by title
node run-pipeline.mjs --record --spec demo/auth-demo.spec.ts \
  --grep "Five Authentication Strategies"

# GOOD: use a unique tag per spec (@auth-demo vs @exec-demo)
node run-pipeline.mjs --record --spec demo/auth-demo.spec.ts \
  --grep @auth-demo
```

### Recovery: Fix After a Bad Recording

If you already ran `--record` with `--grep @demo` and got mixed results:

1. **Find the correct per-test video:**
   ```bash
   ls test-results/   # Each test gets its own folder with video.webm
   # e.g., test-results/auth-strategies-demo-Five--xxxxx-video/video.webm
   ```

2. **Trim captions.json** to only the target spec's entries (check `recording.log` to see where one test ends and another begins — look for the `✓` pass line):
   ```bash
   node -e "
   const c = require('./demo-output/captions.json');
   const trimmed = c.filter(x => x.id <= 52); // adjust ID cutoff
   require('fs').writeFileSync('./demo-output/captions.json', JSON.stringify(trimmed, null, 2));
   "
   ```

3. **Re-merge with correct inputs** (no ElevenLabs credits needed):
   ```bash
   # Merge video + audio (using first 52 audio files)
   node scripts/merge-video.mjs \
     --video test-results/<correct-test>/video.webm \
     --manifest demo-output/captions.json \
     --audio-dir demo-output/audio \
     --output demo-output/demo-with-voice.mp4

   # Add music
   node scripts/add-music.mjs \
     --video demo-output/demo-with-voice.mp4 \
     --music path/to/music.mp3 \
     --output demo-output/demo-final.mp4
   ```

### `--skip-voice`: Reuse Existing Audio

When re-recording or re-merging, use `--skip-voice` to skip ElevenLabs TTS and reuse existing `caption_NN.mp3` files:

```bash
node run-pipeline.mjs --record --skip-voice \
  --spec demo/auth-demo.spec.ts \
  --grep "Five Authentication" \
  --music path/to/music.mp3 \
  --output-dir ./demo-output
```

This re-records the video, re-extracts captions (with new timestamps), and re-merges — but keeps the existing audio files. Useful when:
- You ran out of ElevenLabs credits
- The voiceover is good but the video timing needs adjustment
- You changed the spec's visual flow but not the narration text

## When to Use

- User says "create a demo video", "generate a demo", "playwright demo"
- User wants to convert a Playwright spec into a narrated video
- User wants to add voiceover to an existing video recording
- User wants to auto-discover project features and generate a demo spec
- User wants to extract captions from a Playwright test file

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| ffmpeg + ffprobe | Video/audio processing | `brew install ffmpeg` |
| Node.js 18+ | Pipeline scripts (native fetch) | Required for Playwright |
| Playwright | Video recording | In target project |
| ElevenLabs API key | TTS voice generation | `ELEVENLABS_API_KEY` in `.env` |

## Two Modes

### Mode 1: Guided (User Provides Spec)

User has a Playwright spec with `showCaption()`/`caption()` calls.

**Steps:**

1. Copy templates into the target project:
   - `templates/caption-overlay.ts` -- caption CSS + functions + timestamp recording
   - `templates/demo-helpers.ts` -- pause/scroll/viewport/dragAndDrop helpers
   - `templates/playwright.video.config.ts` -- video recording config
2. **IMPORTANT:** Ensure the spec calls `startTimestampRecording()` as the first line of the test:
   ```typescript
   import { startTimestampRecording, showCaption, caption, hideCaption } from './caption-overlay';

   test('My Demo @demo', async ({ page }) => {
     startTimestampRecording();  // <-- REQUIRED for exact timestamps
     await page.goto('/');
     // ... rest of demo
   });
   ```
3. **Recommended (one command):** Let the pipeline record + process:
   ```bash
   node scripts/run-pipeline.mjs \
     --record \
     --spec path/to/demo.spec.ts \
     --grep "Exact Test Title Here" \
     --music path/to/background.mp3 \
     --output-dir ./demo-output \
     --project-dir /path/to/web-project
   ```
   This runs Playwright, captures timestamp markers from stdout, auto-finds the video, and produces the final MP4 with exact audio-video sync.

   **IMPORTANT:** Always pass `--grep "Exact Test Title"` when multiple `@demo` specs exist in the project. The default `--grep @demo` runs ALL matching specs, causing video/audio mismatch. See "Critical: Multiple `@demo` Specs" section.

4. **Alternative (separate steps):** Record manually, then run pipeline:
   ```bash
   # Record and capture output
   npx playwright test --config=playwright.video.config.ts --grep @demo 2>&1 | tee demo-output/recording.log
   # Run pipeline with captured log
   node scripts/run-pipeline.mjs \
     --spec path/to/demo.spec.ts \
     --video path/to/recording.webm \
     --music path/to/background.mp3 \
     --output-dir ./demo-output
   ```
   If `recording.log` exists in the output dir, extract-captions will auto-detect `__CAPTION_TS__` markers.

### Mode 2: Auto-Discover (Generate Spec from Project)

Scan a project's source code and generate a demo spec automatically.
See [references/auto-discover.md](references/auto-discover.md) for detailed patterns.

**Steps:**

1. Run auto-discover to generate spec and feature inventory:
   ```bash
   node scripts/auto-discover.mjs <project-dir> [options]

   Options:
     --output, -o <path>      Output spec file (default: <project>/demo/auto-demo.spec.ts)
     --inventory <path>       Output feature inventory JSON
     --focus <feature>        Guided mode: focus on specific feature (kanban, charts, etc.)
     --project-name <name>    Override project name
     --dry-run                Print without writing files
     --inventory-only         Only output feature inventory
   ```
2. Review the generated spec -- adjust captions and timing as needed
3. Copy templates into the target project (helpers.ts, caption-overlay.ts, playwright.video.config.ts)
4. Record the video: `npx playwright test --config=playwright.video.config.ts --grep @auto-demo`
5. Run the pipeline on generated spec + recorded video

**What auto-discover detects:**

| Feature | Detection Method | Demo Section |
|---------|-----------------|--------------|
| Framework | package.json dependencies | Tech stack label |
| Routes | React Router `<Route>`, Next.js pages/app, nav configs | Page navigation |
| Stat cards | `testId` prop, `data-testid="stat-*"` | Hover interaction |
| Charts | Recharts/Chart.js/D3 imports + chart test IDs | Scroll + tooltip hover |
| Data tables | `data-testid="*-table"`, sort indicators | Sort column headers |
| Kanban board | `kanban-*` test IDs, draggable attributes | Drag-and-drop cards |
| Dark mode | `theme-toggle` test ID, appearance settings | Toggle + navigate |
| Forms | `*-form`, `*-input`, `invite-*` test IDs | Show section |
| Responsive | Tailwind CSS detected | Mobile/tablet/desktop |
| Settings | Profile, notification, accent color test IDs | Navigate + interact |

**Guided mode:** Pass `--focus <feature>` to generate a spec focused on a single feature. The focus string matches against feature category, label, and description. If no match is found, falls back to full discovery with a warning.

```bash
# Full demo (all features)
node scripts/auto-discover.mjs ./my-project

# Focused on kanban drag-and-drop
node scripts/auto-discover.mjs ./my-project --focus kanban

# Focused on dark mode
node scripts/auto-discover.mjs ./my-project --focus "dark mode"

# Focused on data visualization
node scripts/auto-discover.mjs ./my-project --focus charts
```

## Pipeline Architecture

```
Project source code
  |  auto-discover       Scan framework, routes, features, test IDs
  v                      Generate Playwright spec with captions
Playwright spec (*.spec.ts)
  |  record (optional)   Run Playwright test, capture __CAPTION_TS__ markers
  v                      from startTimestampRecording() -> recording.log
  |  extract-captions    Parse markers for exact timestamps (preferred)
  v                      OR estimate from code heuristic (fallback)
  |  generate-voice      Per-caption ElevenLabs API -> caption_NN.mp3 (cached)
  v
  |  merge-video         Video + audio -> freeze-frame merge -> MP4
  v                      Zero audio overlaps guaranteed
  |  add-music           Voiced MP4 + music -> final MP4 (15% volume, looped)
  v
Final demo.mp4
```

### Timestamp Modes

| Mode | Accuracy | How It Works |
|------|----------|--------------|
| **Real timestamps** (recommended) | Exact | Spec calls `startTimestampRecording()`. Caption functions emit `__CAPTION_TS__` markers to stdout during recording. Pipeline parses these for precise video-aligned timestamps. |
| **Heuristic estimation** (fallback) | +/-1-8s on long demos | `extract-captions.mjs` parses the spec code and estimates timing from `page.goto()`, `waitForTimeout()`, etc. Non-deterministic operations (`waitForLoadState`, network calls) cause cumulative drift. |

**Always prefer real timestamps.** The heuristic mode exists as a fallback for specs that don't use `startTimestampRecording()`, but it will drift on demos longer than ~60s with many navigation/network operations.

## Pipeline Scripts

All scripts live in `scripts/` and use Node.js builtins only (zero npm dependencies).

### scripts/auto-discover.mjs

Scan a project to detect features and generate a Playwright demo spec.

```bash
node scripts/auto-discover.mjs <project-dir> [options]

Options:
  --output, -o <path>      Output spec file (default: <project>/demo/auto-demo.spec.ts)
  --inventory <path>       Feature inventory JSON output
  --focus <feature>        Guided mode: focus on specific feature
  --project-name <name>    Override project name
  --base-url <url>         Dev server URL (default: http://localhost:5173)
  --dry-run                Print without writing files
  --inventory-only         Only output feature inventory
  --helpers-dir <path>     Directory containing helpers.ts
```

**Discovery pipeline:**
1. Read `package.json` to detect framework (React, Next.js, Vue, Angular, Svelte) and build tool
2. Scan for `<Route>` definitions, navItems configs, and file-based routes
3. Grep `data-testid` attributes and `testId` props across all components
4. Detect dynamic test ID patterns (template literals like `` data-testid={`nav-${var}`} ``)
5. Categorize features by demo impact: charts > tables > kanban > dark mode > forms > navigation > responsive > settings
6. Generate a Playwright spec with caption calls compatible with the extract-captions pipeline

**Output:** Feature inventory JSON + Playwright spec file ready for recording.

### scripts/extract-captions.mjs

Parse spec file or recording log, output JSON manifest with captions and timestamps.

```bash
# Recommended: use real timestamps from recording log
node scripts/extract-captions.mjs <spec-file> --from-log recording.log [options]

# Fallback: heuristic estimation from spec code
node scripts/extract-captions.mjs <spec-file> [options]

Options:
  --output, -o <path>      Output JSON manifest path (default: captions.json)
  --from-log <path>        Parse real timestamps from Playwright test output
  --show-fn <name>         Custom showCaption function name
  --caption-fn <name>      Custom caption function name
  --hide-fn <name>         Custom hideCaption function name
  --dry-run                Print manifest to stdout
```

**Two modes:**

| Mode | Flag | Accuracy | When to use |
|------|------|----------|-------------|
| From-log | `--from-log <file>` | Exact | Spec uses `startTimestampRecording()`. Pipeline captures test output. |
| Heuristic | (default) | +/-1-8s | Legacy specs without `startTimestampRecording()`. Drift worsens with demo length. |

**From-log mode** parses `__CAPTION_TS__` markers emitted by `caption-overlay.ts`:
```
__CAPTION_TS__:init:1.0
__CAPTION_TS__:show:17.32:"Authentication is handled by Keycloak"
__CAPTION_TS__:caption:8.15:6000:"Built with Next.js and Spring Boot"
```

**Heuristic mode** uses line-by-line sequential timing estimation. See [references/RESEARCH.md](references/RESEARCH.md) for algorithm details. Known limitation: operations like `page.goto()`, `waitForLoadState()`, network calls, and `expect()` assertions have variable real-world duration that causes cumulative drift.

**Output format:**
```json
[
  { "id": 1, "text": "Welcome to the dashboard.", "startSec": 1.4, "type": "caption", "durationMs": 5000 },
  { "id": 2, "text": "Interactive stat cards.", "startSec": 5.5, "type": "showCaption" }
]
```

The manifest is user-editable before TTS generation -- the safety valve for timestamp corrections.

### scripts/generate-voice.mjs

Per-caption ElevenLabs TTS with caching and voice continuity.

```bash
node scripts/generate-voice.mjs <manifest.json> [options]

Options:
  --output-dir, -d <dir>   Audio output directory (default: ./audio)
  --voice-id <id>          ElevenLabs voice ID (default: Matilda)
  --model <id>             ElevenLabs model (default: eleven_turbo_v2_5)
  --api-key <key>          API key (overrides ELEVENLABS_API_KEY env)
  --dry-run                Print plan without API calls
  --force                  Regenerate all, ignore cache
```

Features:
- **Caching:** Skips generation if `caption_NN.mp3` exists and non-empty
- **Voice continuity:** Sends `previous_text`/`next_text` with every API call
- **Retry:** 3 attempts with exponential backoff (1s, 2s, 4s)
- **Cost estimate:** Prints total character count and credit estimate before starting

### scripts/merge-video.mjs

Freeze-frame merge algorithm (generalized from merge-highlights-v2.mjs).

```bash
node scripts/merge-video.mjs --video <video> --manifest <manifest.json> --audio-dir <dir> [options]

Options:
  --output, -o <path>      Output video path (default: demo-with-voice.mp4)
  --audio-shift <sec>      Voice before visual caption (default: -0.5)
  --min-gap <sec>          Min silence between clips (default: 0.3)
  --crf <n>                Video quality (default: 20)
  --dry-run                Print ffmpeg command only
```

**Golden Rules:**
1. Audio clips NEVER overlap
2. Audio starts 500ms before visual caption (`AUDIO_SHIFT = -0.5`)
3. Minimum 300ms silence gap between clips (`MIN_GAP = 0.3`)
4. Freeze frames via ffmpeg `trim` + `tpad=stop_mode=clone` + `concat`

### scripts/add-music.mjs

Background music overlay.

```bash
node scripts/add-music.mjs --video <voiced.mp4> --music <music.mp3> [options]

Options:
  --output, -o <path>      Output path (default: demo-final.mp4)
  --volume <0-1>           Music volume (default: 0.15 = 15%)
  --fade-out <sec>         Fade music before end (default: 3s)
  --no-loop                Do not loop music
  --dry-run                Print command only
```

Music at 15% volume, looped if shorter than video, `-c:v copy` for fast processing.
Music source: [Pixabay Music](https://pixabay.com/music/) (CC0, no attribution required).

### scripts/run-pipeline.mjs

Orchestrator that chains all steps with pre-flight checks. Supports `--record` mode for single-command workflow.

```bash
# Recommended: record + process in one command
node scripts/run-pipeline.mjs --record --spec <spec.ts> [options]

# Alternative: provide pre-recorded video
node scripts/run-pipeline.mjs --spec <spec.ts> --video <video.webm> [options]

Options:
  --spec, -s <path>        Playwright spec with caption calls
  --video, -v <path>       Recorded video file
  --record                 Run Playwright test, capture output for timestamps
  --playwright-config <p>  Playwright config (default: playwright.video.config.ts)
  --grep <pattern>         Playwright grep pattern (default: @demo)
  --project-dir <path>     Project dir for Playwright (default: cwd)
  --music <path>           Background music (optional)
  --output-dir, -d <dir>   Working directory (default: ./demo-output)
  --output, -o <path>      Final output path
  --skip-voice             Use existing audio files
  --skip-music             Skip music overlay
  --dry-run                Print plan without executing
  (+ all options from individual scripts)
```

**`--record` mode:**
1. Runs `npx playwright test --config=<config> --grep <pattern>` in the project dir
2. Captures stdout to `<output-dir>/recording.log`
3. Auto-finds the video file in `test-results/` (most recent .webm)
4. Detects `__CAPTION_TS__` markers in the log for exact timestamps
5. Falls back to heuristic extraction if no markers found

**WARNING:** `--grep` defaults to `@demo` and runs ALL matching specs. If multiple specs have `@demo`, ALL run and their markers/videos mix. Use a specific grep pattern (e.g., `--grep "My Specific Test Name"`) when multiple demo specs exist. See "Critical: Multiple `@demo` Specs" section above.

Pre-flight checks: ffmpeg, ffprobe, Node.js version, ElevenLabs API key, Playwright (if `--record`).

## Templates

Copy these into your target project.

### templates/caption-overlay.ts

Caption CSS + `showCaption`/`hideCaption`/`caption` functions + `startTimestampRecording()`. When `startTimestampRecording()` is called at the start of a test, each caption function emits `__CAPTION_TS__` markers to stdout that the pipeline parses for exact video-audio sync. The pipeline's extract-captions.mjs parses these function calls, so the naming convention matters.

### templates/demo-helpers.ts

Demo pacing utilities: `pause`, `scenicPause`, `quickPause`, `smoothScroll`, `setViewport`, `naturalType`, `dragAndDrop`. Each has documented internal timing that extract-captions.mjs uses for timestamp estimation.

### templates/playwright.video.config.ts

Playwright config optimized for video recording: headless mode, 1280x800 viewport, generous timeouts, sequential execution, auto-start dev server.

## Caption Extraction Details

### Method: Real Timestamps (Primary) or Regex Heuristic (Fallback)

**Primary method:** `startTimestampRecording()` causes each caption function to emit `__CAPTION_TS__` markers to stdout with `Date.now()`-based timestamps relative to video start. The pipeline parses these for exact alignment. Zero drift regardless of demo length.

**Fallback method:** Regex text extraction + line-by-line heuristic for timestamps. Works without `startTimestampRecording()` but drifts on long demos.

**Why regex (for fallback):** Caption texts are always string literals. The freeze-frame merge compensates for moderate drift. Zero dependencies.

**When to upgrade to AST:** If specs use variables for captions (e.g., `const msg = 'Hello'; showCaption(page, msg)`), add `@babel/parser`.

### Timestamp Estimation Constants

| Function | Duration |
|----------|----------|
| `waitForTimeout(N)` | N/1000 s |
| `pause(page, N)` | N/1000 s |
| `scenicPause(page, N)` | N/1000 s (default 1800ms) |
| `quickPause(page, N)` | N/1000 s (default 600ms) |
| `smoothScroll(...)` | 0.8 s |
| `setViewport(...)` | 0.4 s |
| `dragAndDrop(..., {holdMs})` | holdMs*2 + 300 ms |
| `page.goto(...)` | 1.0 s (estimated) |
| `page.waitForLoadState(...)` | 0.5 s (estimated) |
| `page.click(...)` | 0.1 s |
| `page.hover(...)` | 0.1 s |
| `showCaption(...)` | +0.3 s (fade-in) |
| `hideCaption(...)` | +0.3 s (fade-out) |
| `caption(page, text, ms)` | 0.3 + ms/1000 + 0.3 s |

## Error Handling

### Pre-Flight (Fail Fast)

1. Verify ffmpeg/ffprobe installed
2. Verify ElevenLabs API key set (if voice requested)
3. Verify spec file and video file exist
4. Verify Node.js 18+ (native fetch required)

### Extraction (Degrade Gracefully)

1. Zero captions: warn, suggest `--show-fn`/`--caption-fn` overrides
2. Negative timestamps: clamp to 0
3. Non-monotonic: warn, offer linear interpolation
4. Multiline caption(): handled automatically by whitespace normalization

### Pipeline (Retry or Report)

1. ElevenLabs failure: retry 3x with exponential backoff (1s, 2s, 4s)
2. ffmpeg failure: capture stderr, suggest fixes
3. ffprobe failure: estimate duration from text length

## Reference Files

- **Full research findings**: [references/RESEARCH.md](references/RESEARCH.md) -- AST vs regex analysis, prototype results, algorithm pseudocode
- **Auto-discover patterns**: [references/auto-discover.md](references/auto-discover.md) -- framework detection, feature scanning, spec generation
- **Pipeline patterns**: [references/pipeline-patterns.md](references/pipeline-patterns.md) -- ffmpeg commands, ElevenLabs API, freeze-frame algorithm

## Success Criteria

- Caption extraction matches all showCaption/caption calls in the spec
- With `startTimestampRecording()`: timestamps are exact (within ~1s absolute, 0 relative drift)
- Without: heuristic timestamps within +/-1s for short demos, may drift on long demos
- JSON manifest produced and editable
- Auto-discover identifies major features from project structure
- Pipeline produces working MP4 with synchronized voice and captions
- Audio clips never overlap in the final video

## On Failure

1. **Regex misses captions**: Check function names; try `--show-fn`, `--caption-fn` overrides
2. **Timestamps far off (heuristic mode)**: Add `startTimestampRecording()` to spec and use `--record` mode. This eliminates drift entirely.
3. **No __CAPTION_TS__ markers in log**: Ensure spec imports and calls `startTimestampRecording()` from the updated `caption-overlay.ts` template. The pipeline falls back to heuristic if markers are missing.
4. **Auto-discover empty**: Check data-testid attributes; fall back to guided mode
5. **ffmpeg errors**: Run `ffmpeg -version`; check input file formats; try `--dry-run`
6. **ElevenLabs errors**: Check API key and credits; use `--dry-run` to verify manifest first
7. **Audio overlaps**: Increase `--min-gap`; reduce caption density in spec
8. **Video freezes while audio continues**: Multiple specs ran — see "Critical: Multiple `@demo` Specs" section. Trim `captions.json`, use per-test video, re-merge with `--skip-voice`.
9. **Wrong video content for narration**: `findRecordedVideo()` picked the wrong test's video. Pass `--video <path>` explicitly or use the per-test video from `test-results/<test-folder>/video.webm`.
10. **Too many captions in manifest**: Recording captured markers from multiple specs. Check `recording.log` for the `✓` line marking where your spec ends. Trim `captions.json` to entries before that point.
