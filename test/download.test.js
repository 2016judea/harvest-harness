// /api/download must never hand out the zip on a paid session from some OTHER product
// on the same Stripe account. The zip module only exists in build/, so the handler is
// loaded next to a stub bundle and Stripe is a stubbed fetch — no key, no network.
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, copyFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const dir = mkdtempSync(join(tmpdir(), "hh-download-"));
writeFileSync(join(dir, "_bundle.js"), 'export const ZIP_B64 = "UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA==";\n');
copyFileSync(new URL("../site/api/download.js", import.meta.url), join(dir, "download.js"));
const { default: handler } = await import(pathToFileURL(join(dir, "download.js")).href);

function res() {
  const r = { code: null, body: null, headers: {} };
  r.status = (c) => { r.code = c; return r; };
  r.send = (b) => { r.body = b; return r; };
  r.setHeader = (k, v) => { r.headers[k] = v; };
  return r;
}
const paidOn = (payment_link) => async () => ({ ok: true, json: async () => ({ payment_status: "paid", payment_link }) });
const req = { query: { session_id: "cs_live_abc123" } };

test("unset PAYMENT_LINK_ID fails closed, even for a paid session", async () => {
  delete process.env.PAYMENT_LINK_ID;
  globalThis.fetch = paidOn("plink_other_product");
  const r = res();
  await handler(req, r);
  assert.equal(r.code, 500);
  assert.notEqual(r.headers["Content-Type"], "application/zip");
});

test("a paid session on another payment link is refused", async () => {
  process.env.PAYMENT_LINK_ID = "plink_harness";
  globalThis.fetch = paidOn("plink_other_product");
  const r = res();
  await handler(req, r);
  assert.equal(r.code, 402);
});

test("a paid session on the harness link streams the zip", async () => {
  process.env.PAYMENT_LINK_ID = "plink_harness";
  globalThis.fetch = paidOn("plink_harness");
  const r = res();
  await handler(req, r);
  assert.equal(r.code, 200);
  assert.equal(r.headers["Content-Type"], "application/zip");
});

test("a malformed session id never reaches Stripe", async () => {
  process.env.PAYMENT_LINK_ID = "plink_harness";
  globalThis.fetch = async () => { throw new Error("must not be called"); };
  const r = res();
  await handler({ query: { session_id: "../etc" } }, r);
  assert.equal(r.code, 400);
});
