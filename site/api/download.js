// GET /api/download?session_id=cs_... : verify the Checkout Session is paid and came from
// our payment link, then stream the zip. The zip is bundled into this function (_bundle.js),
// never served as a static file.
import { ZIP_B64 } from "./_bundle.js";

export default async function handler(req, res) {
  const id = String((req.query && req.query.session_id) || "");
  if (!/^cs_(live|test)_[A-Za-z0-9]+$/.test(id)) return res.status(400).send("Missing or malformed session_id.");
  const r = await fetch(`https://api.stripe.com/v1/checkout/sessions/${id}`, {
    headers: { Authorization: `Bearer ${process.env.STRIPE_SECRET_KEY}` },
  });
  if (!r.ok) return res.status(404).send("No such purchase.");
  const s = await r.json();
  const link = process.env.PAYMENT_LINK_ID;
  if (s.payment_status !== "paid" || (link && s.payment_link !== link)) {
    return res.status(402).send("This purchase is not paid yet.");
  }
  const buf = Buffer.from(ZIP_B64, "base64");
  res.setHeader("Content-Type", "application/zip");
  res.setHeader("Content-Disposition", 'attachment; filename="harness.zip"');
  res.setHeader("Cache-Control", "private, no-store");
  res.status(200).send(buf);
}
