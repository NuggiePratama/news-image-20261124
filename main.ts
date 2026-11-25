// Entry point: renders entry.png with the Python renderer and validates it.
// No network, no model calls. Deterministic: the same run always writes
// the same PNG bytes.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const png = join(dir, "entry.png");

function fail(msg) {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
}

const run = spawnSync("python3", [join(dir, "render.py")], {
  encoding: "utf8",
  stdio: ["ignore", "pipe", "pipe"],
});
if (run.status !== 0) fail(`render.py exited ${run.status}: ${run.stderr}`);
console.log(run.stdout.trim());

if (!existsSync(png)) fail("entry.png missing after render");
const size = statSync(png).size;
if (size < 50_000) fail(`entry.png suspiciously small: ${size} bytes`);

const buf = readFileSync(png);
// Parse the PNG IHDR chunk: width and height must be 1024x1024.
if (buf.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") {
  fail("entry.png is not a PNG");
}
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  fail(`entry.png is ${width}x${height}, expected 1024x1024`);
}
console.log(`OK: entry.png ${width}x${height}, ${size} bytes`);
