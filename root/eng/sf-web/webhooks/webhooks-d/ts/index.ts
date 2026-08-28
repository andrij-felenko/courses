import express from "express";
import crypto from "node:crypto";

const app = express();
const SECRET = process.env.WEBHOOK_SECRET!;
const seen = new Set<string>();          // насправді — стійке сховище, не пам'ять

// важливо: сирі байти тіла, а не розібраний JSON
app.post("/webhooks", express.raw({ type: "application/json" }), (req, res) => {
  const sig = req.header("X-Signature") ?? "";
  const expected = crypto.createHmac("sha256", SECRET)
    .update(req.body)                    // req.body — Buffer сирих байтів
    .digest("hex");
  // порівняння сталого часу — щоб через час відповіді не витік підпис
  const ok = sig.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected));
  if (!ok) return res.sendStatus(401);

  const event = JSON.parse(req.body.toString("utf8"));
  if (seen.has(event.id)) return res.sendStatus(200);   // вже бачили — тихо
  seen.add(event.id);

  queue.push(event);                     // зняти роботу з гарячого шляху
  return res.sendStatus(200);            // підтвердити ОДРАЗУ
});
