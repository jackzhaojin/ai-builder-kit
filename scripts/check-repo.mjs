#!/usr/bin/env node
// Checks the repo conventions in CLAUDE.md that `claude plugin validate` does not know about.
// Zero dependencies. Run from anywhere:
//
//   node scripts/check-repo.mjs                 # conventions only
//   node scripts/check-repo.mjs --base <ref>    # also require a version bump on plugins whose
//                                               # files (or symlinked skills) changed since <ref>
//
// Exit 1 on any error. Warnings print but do not fail.

import { execFileSync } from 'node:child_process';
import { existsSync, lstatSync, readFileSync, readdirSync, realpathSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const MAX_SKILL_LINES = 500;
const FORBIDDEN_IN_SKILLS = /(^|\/)(\.venv|node_modules|__pycache__)\/|(^|\/)pyproject\.toml$/;

const errors = [];
const warnings = [];
const error = (msg) => errors.push(msg);
const warn = (msg) => warnings.push(msg);

const git = (...args) => execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' }).trim();
const readJson = (rel) => JSON.parse(readFileSync(join(ROOT, rel), 'utf8'));
const tracked = git('ls-files').split('\n').filter(Boolean);

const baseArg = process.argv.indexOf('--base');
let base = baseArg > -1 ? process.argv[baseArg + 1] ?? '' : '';
// A push that creates a branch reports an all-zero "before" SHA, and a shallow clone may not have
// the base at all. Either way there is nothing to diff against.
if (base) {
  try {
    git('rev-parse', '--verify', '--quiet', `${base}^{commit}`);
  } catch {
    warn(`--base ${base} is not a commit in this clone, skipping the version-bump check`);
    base = '';
  }
}

// --- every tracked JSON file parses -------------------------------------------------------------
for (const f of tracked.filter((f) => f.endsWith('.json'))) {
  try {
    readJson(f);
  } catch (e) {
    error(`${f}: invalid JSON (${e.message})`);
  }
}

// --- skills/ -----------------------------------------------------------------------------------
function frontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return null;
  const fields = {};
  let key = null;
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([a-z][a-z0-9-]*):\s*(.*)$/);
    if (kv) {
      key = kv[1];
      // Block scalars (>, |, >-) start empty and continue on the indented lines below.
      fields[key] = /^[>|][+-]?$/.test(kv[2]) ? '' : kv[2].replace(/^["']|["']$/g, '');
    } else if (key && /^\s+\S/.test(line)) {
      fields[key] = `${fields[key]} ${line.trim()}`.trim();
    }
  }
  return fields;
}

const marketplace = readJson('.claude-plugin/marketplace.json');
const readme = readFileSync(join(ROOT, 'README.md'), 'utf8');
const skillDirs = readdirSync(join(ROOT, 'skills'), { withFileTypes: true })
  .filter((d) => d.isDirectory() && !d.name.endsWith('-workspace'))
  .map((d) => d.name)
  .filter((name) => tracked.some((f) => f.startsWith(`skills/${name}/`)));

for (const name of skillDirs) {
  const skillMd = `skills/${name}/SKILL.md`;
  if (!existsSync(join(ROOT, skillMd))) {
    error(`${skillMd}: missing`);
    continue;
  }
  const text = readFileSync(join(ROOT, skillMd), 'utf8');
  const fm = frontmatter(text);
  if (!fm) {
    error(`${skillMd}: no YAML frontmatter`);
  } else {
    if (fm.name !== name) error(`${skillMd}: frontmatter name "${fm.name}" does not match folder "${name}"`);
    if (!fm.description) error(`${skillMd}: frontmatter has no description`);
    else if (!/\b(use (this|when|whenever|it)|trigger)/i.test(fm.description))
      error(`${skillMd}: description has no trigger phrase ("Use when the user says...")`);
  }
  const lines = text.split('\n').length;
  if (lines > MAX_SKILL_LINES) error(`${skillMd}: ${lines} lines, keep it under ${MAX_SKILL_LINES} and move detail to references/`);

  const entries = marketplace.plugins.filter((p) => p.source === `./skills/${name}`);
  if (entries.length !== 1) {
    error(`.claude-plugin/marketplace.json: expected one entry with source ./skills/${name}, found ${entries.length}`);
  } else {
    const e = entries[0];
    if (e.name !== name) error(`.claude-plugin/marketplace.json: entry for ./skills/${name} is named "${e.name}"`);
    if (e.strict !== false) error(`.claude-plugin/marketplace.json: ${name} needs "strict": false (bare skill folder, no plugin.json)`);
    if ('version' in e) error(`.claude-plugin/marketplace.json: ${name} must not set version (updates key on the commit SHA)`);
  }

  if (!readme.includes(`[${name}](skills/${name}/)`)) error(`README.md: no table row for ${name}`);

  for (const f of tracked.filter((f) => f.startsWith(`skills/${name}/`) && FORBIDDEN_IN_SKILLS.test(f)))
    error(`${f}: never commit a venv, node_modules or pyproject.toml inside a skill`);
}

// --- marketplace entries point at real folders --------------------------------------------------
for (const e of marketplace.plugins) {
  if (typeof e.source !== 'string') continue;
  if (!existsSync(join(ROOT, e.source))) error(`.claude-plugin/marketplace.json: ${e.name} source ${e.source} does not exist`);
}

// --- plugins/ (hook bundles) ---------------------------------------------------------------------
const pluginDirs = existsSync(join(ROOT, 'plugins'))
  ? readdirSync(join(ROOT, 'plugins'), { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name)
  : [];

// Files outside plugins/<name>/ that a plugin pulls in through symlinks, keyed by plugin name.
const linkedPaths = {};

function walkLinks(dir, plugin) {
  for (const d of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, d.name);
    if (lstatSync(p).isSymbolicLink()) {
      const rel = relative(ROOT, p);
      if (!existsSync(p)) {
        error(`${rel}: symlink target does not exist`);
        continue;
      }
      const target = relative(ROOT, realpathSync(p));
      if (target.startsWith('..')) error(`${rel}: symlink points outside the repo (${target}); marketplace installs skip it`);
      else (linkedPaths[plugin] ??= []).push(target);
    } else if (d.isDirectory()) {
      walkLinks(p, plugin);
    }
  }
}

for (const name of pluginDirs) {
  const dir = `plugins/${name}`;
  const manifestPath = `${dir}/.claude-plugin/plugin.json`;
  if (!existsSync(join(ROOT, manifestPath))) {
    error(`${manifestPath}: missing`);
    continue;
  }
  const manifest = readJson(manifestPath);
  if (manifest.name !== name) error(`${manifestPath}: name "${manifest.name}" does not match folder "${name}"`);
  // A symlinked skill changes without touching this folder, so the commit SHA of the folder does
  // not move. An explicit version is the only way installs see the update.
  if (!manifest.version) error(`${manifestPath}: hook plugins carry an explicit version`);

  const entry = marketplace.plugins.find((p) => p.source === `./${dir}`);
  if (!entry) error(`.claude-plugin/marketplace.json: no entry for ./${dir}`);
  else if ('version' in entry) error(`.claude-plugin/marketplace.json: ${name} sets version, keep it only in ${manifestPath}`);

  if (!readme.includes(`[${name}](${dir}/)`)) error(`README.md: no table row for ${name}`);

  walkLinks(join(ROOT, dir), name);

  for (const f of tracked.filter((f) => f.startsWith(`${dir}/hooks/`) && f.endsWith('.sh'))) {
    if (!(statSync(join(ROOT, f)).mode & 0o111)) error(`${f}: hook script is not executable`);
  }

  if (base) {
    let baseVersion = null;
    try {
      baseVersion = JSON.parse(git('show', `${base}:${manifestPath}`)).version;
    } catch {
      // New plugin, or the base predates it: nothing to compare.
    }
    const watched = [dir, ...(linkedPaths[name] ?? [])];
    const changed = git('diff', '--name-only', `${base}...HEAD`, '--', ...watched).split('\n').filter(Boolean)
      .concat(git('diff', '--name-only', 'HEAD', '--', ...watched).split('\n').filter(Boolean));
    if (baseVersion && changed.length && baseVersion === manifest.version)
      error(`${manifestPath}: ${changed.length} file(s) changed since ${base} (${changed[0]}...) but version is still ${baseVersion}`);
  }
}

// --- Codex and portable manifests agree with each other -------------------------------------------
const codex = readJson('.codex-plugin/plugin.json');
const portable = readJson('plugin.json');
for (const key of ['name', 'version', 'description', 'license', 'homepage']) {
  if (codex[key] !== portable[key]) error(`.codex-plugin/plugin.json and plugin.json disagree on ${key}`);
}
if (marketplace.version && marketplace.version !== codex.version)
  error(`.claude-plugin/marketplace.json version ${marketplace.version} does not match bundle version ${codex.version}`);
const codexMarket = readJson('.agents/plugins/marketplace.json');
if (!codexMarket.plugins.some((p) => p.name === codex.name)) error(`.agents/plugins/marketplace.json: no entry for ${codex.name}`);

// --- scripts parse ------------------------------------------------------------------------------
for (const f of tracked.filter((f) => /\.(mjs|js)$/.test(f))) {
  try {
    execFileSync(process.execPath, ['--check', join(ROOT, f)], { stdio: 'pipe' });
  } catch (e) {
    error(`${f}: node --check failed\n${e.stderr}`);
  }
}
for (const f of tracked.filter((f) => f.endsWith('.sh'))) {
  try {
    execFileSync('bash', ['-n', join(ROOT, f)], { stdio: 'pipe' });
  } catch (e) {
    error(`${f}: bash -n failed\n${e.stderr}`);
  }
}

// --- README dates (advisory) --------------------------------------------------------------------
for (const name of skillDirs) {
  const row = readme.match(new RegExp(`\\[${name}\\]\\(skills/${name}/\\) \\| (\\d{4}-\\d{2}-\\d{2})`));
  const last = git('log', '-1', '--format=%cs', '--', `skills/${name}`);
  if (row && last && last > row[1]) warn(`README.md: ${name} Last Modified ${row[1]}, last commit ${last}`);
}

for (const w of warnings) console.log(`warn  ${w}`);
for (const e of errors) console.log(`error ${e}`);
console.log(`\n${skillDirs.length} skills, ${pluginDirs.length} hook plugin(s): ${errors.length} error(s), ${warnings.length} warning(s)`);
process.exit(errors.length ? 1 : 0);
