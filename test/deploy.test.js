// The paid zip (api/_bundle.js) must never be a static URL. 2026-10-19: with outputDirectory "."
// /api/%5Fbundle.js and /%61pi/_bundle.js served the whole $49 harness as base64 (200, 119 KB).
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const read = (f) => readFileSync(new URL(`../${f}`, import.meta.url), "utf8");

test("only public/ is served, in vercel.json and in the deploy payload", () => {
  assert.equal(JSON.parse(read("site/vercel.json")).outputDirectory, "public");
  const deploy = read("scripts/deploy.py");
  assert.match(deploy, /"outputDirectory": "public"/);
  assert.doesNotMatch(deploy, /"outputDirectory": "\."/);
});

test("static files go up under public/, api/ stays outside it", () => {
  const deploy = read("scripts/deploy.py");
  assert.match(deploy, /return "public\/" \+ str\(rel\)/);
  assert.match(deploy, /"file": upload_name\(/);
});
