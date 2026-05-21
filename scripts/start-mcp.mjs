#!/usr/bin/env node

// Launches the JobSpy MCP server using the plugin's Python venv.
// Called by plugin.json's mcpServers config as the MCP server entry point.
// Uses Node.js (not bash) for reliable cross-platform process spawning.

import { existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const pluginRoot = join(__dirname, '..');
const mcpDir = join(pluginRoot, 'mcp');
const venvDir = join(mcpDir, '.venv');
const server = join(mcpDir, 'job_server.py');

const log = (msg) => process.stderr.write(`[jobfinder-mcp] ${msg}\n`);

// Find venv Python — Windows first, then Unix
const candidates = [
  join(venvDir, 'Scripts', 'python.exe'),  // Windows
  join(venvDir, 'bin', 'python'),           // Unix
];

const pythonPath = candidates.find((p) => existsSync(p));

if (!pythonPath) {
  log(`Python venv not found at ${venvDir}. Run ensure-deps first.`);
  log(`Checked: ${candidates.join(', ')}`);
  process.exit(1);
}

if (!existsSync(server)) {
  log(`job_server.py not found at ${server}`);
  process.exit(1);
}

log(`Starting MCP server: ${pythonPath} ${server}`);

// Spawn Python as a child process, piping stdio through to Claude Code
const child = spawn(pythonPath, [server], {
  stdio: ['pipe', 'pipe', 'pipe'],
  cwd: mcpDir,
});

// Pipe stdin/stdout for MCP stdio transport
process.stdin.pipe(child.stdin);
child.stdout.pipe(process.stdout);

// Forward Python's stderr to our stderr (for logging)
child.stderr.on('data', (data) => {
  process.stderr.write(data);
});

child.on('error', (err) => {
  log(`Failed to start Python process: ${err.message}`);
  process.exit(1);
});

child.on('exit', (code, signal) => {
  if (signal) {
    log(`Python process killed by signal: ${signal}`);
  } else if (code !== 0) {
    log(`Python process exited with code: ${code}`);
  }
  process.exit(code ?? 1);
});

// Forward signals to child
process.on('SIGTERM', () => child.kill('SIGTERM'));
process.on('SIGINT', () => child.kill('SIGINT'));
