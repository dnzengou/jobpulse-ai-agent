#!/usr/bin/env node

// SessionStart hook — installs Python dependencies into a venv.
// Skips if venv exists and requirements.txt hash matches cached hash.
// Uses Node.js (not bash) for reliable cross-platform execution.
// Mirrors the pattern from the YouTube plugin's ensure-deps.mjs.

import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { spawnSync } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { createHash } from 'crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const pluginRoot = join(__dirname, '..');
const mcpDir = join(pluginRoot, 'mcp');
const venvDir = join(mcpDir, '.venv');
const requirements = join(mcpDir, 'requirements.txt');
const hashFile = join(venvDir, '.requirements-hash');

const log = (msg) => process.stderr.write(`[jobfinder] ${msg}\n`);

// --- Hash check: skip if deps are already installed ---

function fileHash(filePath) {
  if (!existsSync(filePath)) return null;
  return createHash('sha256').update(readFileSync(filePath)).digest('hex');
}

if (!existsSync(requirements)) {
  log(`requirements.txt not found at ${requirements}`);
  process.exit(0);
}

const currentHash = fileHash(requirements);

if (existsSync(hashFile)) {
  try {
    if (readFileSync(hashFile, 'utf8').trim() === currentHash) {
      // Hash matches — deps are current, skip install
      process.exit(0);
    }
  } catch {}
}

// --- Find a working Python >= 3.10 ---

function findPython() {
  // On Windows, 'python' is the real one; 'python3' is often the Store stub.
  // Don't use shell:true — it mangles Python expressions with curly braces.
  const candidates = process.platform === 'win32'
    ? ['python', 'python3']
    : ['python3', 'python'];

  const versionScript = 'import sys; print(str(sys.version_info.major)+"."+str(sys.version_info.minor))';

  for (const cmd of candidates) {
    try {
      const result = spawnSync(cmd, ['-c', versionScript], {
        encoding: 'utf8',
        timeout: 10_000,
        windowsHide: true,
      });

      if (result.status === 0 && result.stdout) {
        const version = result.stdout.trim();
        const [major, minor] = version.split('.').map(Number);
        if (major >= 3 && minor >= 10) {
          log(`Found Python ${version} via '${cmd}'`);
          return cmd;
        }
        log(`Skipping '${cmd}' — version ${version} < 3.10`);
      }
    } catch {}
  }
  return null;
}

const pythonCmd = findPython();
if (!pythonCmd) {
  log('Python 3.10+ not found. Install Python to use this plugin.');
  process.exit(0);
}

// --- Create venv if needed ---

if (!existsSync(venvDir)) {
  log('Creating Python virtual environment...');
  const venvResult = spawnSync(pythonCmd, ['-m', 'venv', venvDir], {
    encoding: 'utf8',
    timeout: 60_000,
    windowsHide: true,
  });

  if (venvResult.error || venvResult.status !== 0) {
    log('Failed to create venv.');
    if (venvResult.stderr) log(venvResult.stderr);
    process.exit(0);
  }
}

// --- Find pip in venv ---

const pipCandidates = [
  join(venvDir, 'Scripts', 'pip.exe'),  // Windows
  join(venvDir, 'bin', 'pip'),           // Unix
];
const pipPath = pipCandidates.find((p) => existsSync(p));

if (!pipPath) {
  log(`pip not found in venv. Checked: ${pipCandidates.join(', ')}`);
  process.exit(0);
}

// --- Install dependencies ---

log('Installing Python dependencies...');

const installResult = spawnSync(pipPath, ['install', '-r', requirements, '--quiet'], {
  cwd: mcpDir,
  encoding: 'utf8',
  timeout: 120_000,
  windowsHide: true,
});

if (installResult.stdout) process.stderr.write(installResult.stdout);
if (installResult.stderr) process.stderr.write(installResult.stderr);

if (installResult.error || installResult.status !== 0) {
  log('Dependency install failed. MCP tools may not work.');
  process.exit(0);
}

// --- Write hash marker ---

try {
  writeFileSync(hashFile, currentHash);
} catch {}

log('Dependencies ready.');
